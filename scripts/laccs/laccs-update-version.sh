#!/bin/bash

[ -d "/opt/LACCS.old" ] && rm -rf /opt/LACCS.old
mv /opt/LACCS /opt/LACCS.old
tar xf ./*_release.tar.gz -C /opt
cp -f /opt/LACCS.old/Controls/lib* /opt/LACCS/Controls/
cp -f /opt/LACCS.old/configs/node.config /opt/LACCS/configs/
strings /opt/LACCS/LACCS | grep "Ver\..*"

