#!/bin/sh
set -e

# update and upgrade apt
echo "update and upgrade apt"
sudo cp sources.list /etc/apt/sources.list
sudo cp raspi.list /etc/apt/sources.list.d/raspi.list
sudo apt update
sudo apt upgrade

echo "install and setup wvdial"
sudo apt install wvdial
sudo cp wvdial.conf /etc/wvdial.conf

echo "intalling pip packages"
python3 -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple --upgrade pip
pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip3 install --upgrade pycryptodome
pip3 install -U co-python-sdk-v5

echo "setting up services"
sudo cp dial.service /usr/lib/systemd/system/
sudo systemctl enable dial.service

sudo cp test.service /usr/lib/systemd/system/
sudo systemctl enable test.service


echo "create data dir"
mkdir data

echo "rebooting"
sudo reboot

