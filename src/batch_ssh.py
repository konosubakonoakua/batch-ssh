import os
import argparse
import paramiko
import threading
import concurrent.futures
from datetime import datetime
from rich.console import Console
from rich.table import Table

console = Console()
logs = []
log_lock = threading.Lock()

# create logs directory if missing
os.makedirs("logs", exist_ok=True)

# unique log file for this batch run
timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
log_file_path = os.path.join("logs", f"batch-{timestamp}.log")


def log_step(host: str, message: str, ok: bool = True):
    """Thread-safe logging with [ip] prefix."""
    symbol = "✓" if ok else "✗"
    color = "green" if ok else "red"
    line = f"[cyan][{host}][/cyan] [{color}]{symbol} {message}[/{color}]"
    plain_line = f"[{host}] {symbol} {message}"

    with log_lock:
        logs.append(line)
        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(plain_line + "\n")
    console.print(line)


def run_on_host(host, scripts, files, remote_dir, cleanup, ssh_user, ssh_pass, ssh_key):
    results = []
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        log_step(host, f"Connecting to {host}...")
        if ssh_key:
            key = paramiko.RSAKey.from_private_key_file(ssh_key)
            ssh.connect(host, username=ssh_user, pkey=key, timeout=10)
        else:
            ssh.connect(host, username=ssh_user, password=ssh_pass, timeout=10)
        sftp = ssh.open_sftp()

        ssh.exec_command(f"mkdir -p {remote_dir}")
        log_step(host, f"Created batch dir {remote_dir}")

        # Upload files
        for f in files:
            if not os.path.exists(f):
                results.append((host, f, False, "Local file not found"))
                log_step(host, f"Local file {f} not found", ok=False)
                continue
            remote_path = f"{remote_dir}/{os.path.basename(f)}"
            sftp.put(f, remote_path)
            results.append((host, f, True, f"Uploaded to {remote_path}"))
            log_step(host, f"Uploaded {f} -> {remote_path}")

        # Upload and execute scripts
        for script in scripts:
            if not os.path.exists(script):
                results.append((host, script, False, "Local script not found"))
                log_step(host, f"Local script {script} not found", ok=False)
                break
            remote_path = f"{remote_dir}/{os.path.basename(script)}"
            sftp.put(script, remote_path)
            sftp.chmod(remote_path, 0o755)
            log_step(host, f"Uploaded script {script}")

            stdin, stdout, stderr = ssh.exec_command(f"cd {remote_dir} && bash {remote_path}")
            exit_code = stdout.channel.recv_exit_status()
            out = stdout.read().decode()
            err = stderr.read().decode()

            if exit_code != 0:
                results.append((host, script, False, f"Exit {exit_code}, stderr: {err.strip()}"))
                log_step(host, f"Script {script} failed (exit {exit_code})", ok=False)
                break
            else:
                results.append((host, script, True, out.strip()))
                log_step(host, f"Script {script} executed successfully")

        if cleanup:
            ssh.exec_command(f"rm -rf {remote_dir}")
            results.append((host, remote_dir, True, "Remote batch directory removed"))
            log_step(host, f"Cleaned up {remote_dir}")

        sftp.close()
        ssh.close()
    except Exception as e:
        results.append((host, None, False, f"Connection error: {str(e)}"))
        log_step(host, f"Connection error: {str(e)}", ok=False)

    return results


def main(ip_list, scripts, files, remote_dir, cleanup, max_workers, ssh_user, ssh_pass, ssh_key):
    summary = {}

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(run_on_host, ip, scripts, files, remote_dir, cleanup, ssh_user, ssh_pass, ssh_key): ip
            for ip in ip_list
        }
        for future in concurrent.futures.as_completed(futures):
            host = futures[future]
            try:
                results = future.result()
                summary[host] = results
                log_step(host, "Completed successfully")
            except Exception as e:
                summary[host] = [(host, None, False, f"Unhandled error: {str(e)}")]
                log_step(host, f"Error: {e}", ok=False)

    # Final summary table
    table = Table(title="Execution Summary")
    table.add_column("Host", style="cyan")
    table.add_column("Target", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Message", style="yellow")

    for host, results in summary.items():
        for h, target, ok, msg in results:
            status = "[green]✅ SUCCESS[/green]" if ok else "[red]❌ FAIL[/red]"
            table.add_row(host, str(target), status, msg)

    console.print(table)

    # Append summary to log file
    with open(log_file_path, "a", encoding="utf-8") as f:
        f.write("\nExecution Summary:\n")
        for host, results in summary.items():
            for _, target, ok, msg in results:
                status = "SUCCESS" if ok else "FAIL"
                f.write(f"{host}\t{target}\t{status}\t{msg}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch SSH executor with file upload")
    parser.add_argument("ip_file", help="File containing list of IP addresses")
    parser.add_argument("--scripts", nargs="*", default=[], help="Script files to execute on remote")
    parser.add_argument("--files", nargs="*", default=[], help="Files to upload to remote batch dir")
    parser.add_argument("--remote-dir", default=f"/tmp/batch-{timestamp}", help="Remote directory for uploads and scripts")
    parser.add_argument("--cleanup", action="store_true", help="Delete the remote batch directory after execution")
    parser.add_argument("--workers", type=int, default=20, help="Max parallel workers")
    parser.add_argument("--ssh-user", default="root", help="SSH username")
    parser.add_argument("--ssh-pass", default="imp", help="SSH password (ignored if key is provided)")
    parser.add_argument("--ssh-key", default=None, help="Path to private key for SSH authentication")
    args = parser.parse_args()

    with open(args.ip_file) as f:
        ip_list = [line.strip() for line in f if line.strip()]

    main(ip_list, args.scripts, args.files, args.remote_dir, args.cleanup, args.workers,
         args.ssh_user, args.ssh_pass, args.ssh_key)
