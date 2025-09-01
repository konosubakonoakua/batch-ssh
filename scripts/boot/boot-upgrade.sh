#!/bin/bash

cd "$(dirname "$0")" || exit 1
tar xf ./boot.7.3.tgz -C /boot
