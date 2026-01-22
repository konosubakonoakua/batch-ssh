#!/bin/bash

cd "$(dirname "$0")" || exit 1
cp -f ./LACCS /opt/LACCS/LACCS
sed -i '5a\user_server = 10.10.90.179' /opt/LACCS/configs/node.config
