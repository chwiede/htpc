#!/bin/sh

# go to work dir
cd $1

mkdir -p ./tbs-linux-drivers
sudo rm -R ./tbs-linux-drivers/*
unzip $2 -d ./tbs-linux-drivers
cd ./tbs-linux-drivers

tar xjvf linux-tbs-drivers.tar.bz2
cd linux-tbs-drivers

sudo ./v4l/tbs-x86_64.sh
sudo make
sudo rm -R /lib/modules/$(uname -r)/kernel/drivers/media
sudo make install
