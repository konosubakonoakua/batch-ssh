mkdir -p /opt/bistreams/bin
tar xf ./fpgatool.tgz -C /opt/bitstreams/bin
chmod +x /opt/bitstreams/bin/*

tee /etc/systemd/system/load-fpga-bitstream.service > /dev/null << 'EOF'
[Unit]
Description=Load FPGA bitstream with fpgautil
After=local-fs.target
Before=multi-user.target
ConditionPathExists=/opt/bitstreams/current.bit.bin

[Service]
Type=oneshot
ExecStart=/opt/bitstreams/bin/fpgautil -b /opt/bitstreams/current.bit.bin
RemainAfterExit=yes
TimeoutSec=30

[Install]
WantedBy=multi-user.target
EOF
