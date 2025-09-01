sed -i 's/#NTP=/NTP=10.10.7.11/' /etc/systemd/timesyncd.conf
systemctl restart systemd-timesyncd
timedatectl status
