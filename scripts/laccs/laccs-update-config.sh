#!/bin/bash

CONFIG_FILE="/opt/LACCS/configs/node.config"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
  echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
  echo -e "${RED}[ERROR]${NC} $1"
}

check_config_file() {
  if [ ! -f "$CONFIG_FILE" ]; then
    log_error "Config file $CONFIG_FILE does not exist"
    exit 1
  fi
  log_info "Found config file: $CONFIG_FILE"
}

backup_config() {
  local backup_file="${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
  cp "$CONFIG_FILE" "$backup_file"
  log_info "Config file backed up to: $backup_file"
}

get_local_ip() {
  local ip=$(hostname -I | awk '{print $1}')
  if [ -z "$ip" ]; then
    log_error "Cannot get local IP address"
    exit 1
  fi
  echo "$ip"
}

# Update configuration using sed
update_config() {
  local key="$1"
  local value="$2"

  # Escape sed special characters
  local escaped_value=$(echo "$value" | sed 's/[\/&]/\\&/g')

  if grep -q "^[[:space:]]*$key[[:space:]]*=" "$CONFIG_FILE"; then
    # If config item exists, update it
    sed -i "s/^[[:space:]]*$key[[:space:]]*=.*/$key=$escaped_value/" "$CONFIG_FILE"
    log_info "Updated: $key = $value"
  elif grep -q "^[[:space:]]*#$key[[:space:]]*=" "$CONFIG_FILE"; then
    # If config item is commented, uncomment and update
    sed -i "s/^[[:space:]]*#$key[[:space:]]*=.*/$key=$escaped_value/" "$CONFIG_FILE"
    log_info "Uncommented and updated: $key = $value"
  else
    # If config item doesn't exist, append to end of file
    echo "$key=$escaped_value" >>"$CONFIG_FILE"
    log_info "Added: $key = $value"
  fi
}

# Main function
main() {
  log_info "Starting LACCS node configuration..."

  # Check config file
  check_config_file

  # Backup config file
  backup_config

  # Get local IP
  local local_ip=$(get_local_ip)
  log_info "Detected local IP: $local_ip"

  # Update configuration items
  log_info "Updating configuration parameters..."

  # Basic configuration
  update_config "ip_pattern" "$local_ip"
  update_config "scheduler_threads" "64"
  update_config "control_threads" "8"
  update_config "python_threads" "0"
  update_config "epics_link_threads" "0"
  update_config "epics_sever_threads" "0"

  # Database configuration
  update_config "db_server_ip" "10.10.8.222,10.10.90.179,10.10.8.224"
  update_config "db_user" "laccs_nodes"
  update_config "db_password" "Laccs@imp@31415"
  update_config "manager_server_ip" "10.10.8.221,10.10.90.170"

  # Advanced configuration (uncomment and set)
  update_config "cv_init_trigger" "on"
  update_config "empty_handler" "off"
  update_config "accept_ips" "10.10.1.0,10.10.90.0,10.10.7.0,10.10.8.0,10.10.9.0,10.10.101.37,10.10.101.38,10.10.101.39,10.10.101.35"

  log_info "Configuration completed!"

  # Display updated configuration summary
  echo
  log_info "=== Updated Configuration Summary ==="
  grep -E "^(ip_pattern|scheduler_threads|control_threads|python_threads|epics_link_threads|epics_sever_threads|db_server_ip|db_user|db_password|manager_server_ip|cv_init_trigger|empty_handler|accept_ips)=" "$CONFIG_FILE" | while read line; do
    echo "  $line"
  done
}

# Execute main function
main "$@"
