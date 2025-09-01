python ../src/batch_ssh.py ./archives/ip/ip-hiaf-blm.txt \
  --scripts \
  ../scripts/boot/boot-clean.sh \
  ../scripts/boot/boot-upgrade.sh \
  ../scripts/system/sys-reboot.sh \
  --files \
  ../archives/boot/blm.boot.7.3.tgz
