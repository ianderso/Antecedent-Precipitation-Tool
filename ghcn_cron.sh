#!/bin/bash

#Pre-download the entire ghcn daily fileset

mkdir -p /root/ghcn
cd /root/ghcn
wget ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/daily/ghcnd_all.tar.gz
tar -xzf ghcnd_all.tar.gz 
find /root/ghcn/ghcnd_all -name "*.dly" -exec mv {} /usr/share/httpd/.local/share/ulmo/ncdc/ghcn_daily/ \;
chown -R apache:apache /usr/share/httpd/.local/share/ulmo/ncdc/ghcn_daily
rm -Rf /root/ghcn
