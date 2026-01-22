mkdir -p /opt/bitstreams

tar xf ./blm_fpga_*.bit.bin.tgz

filename=$(ls ./blm_fpga_*.bit.bin | head -n 1)
filename=$(basename "$filename")

mv $filename /opt/bitstreams/

ln -s "/opt/bitstreams/$filename" /opt/bitstreams/current.bit.bin
