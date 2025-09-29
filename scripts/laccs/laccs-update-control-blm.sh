#!/bin/bash

cd "$(dirname "$0")" || exit 1
mv /opt/LACCS/Controls/libBeamLossMonitor.so* /tmp
cp -f ./libBeamLossMonitor.so* /opt/LACCS/Controls/
