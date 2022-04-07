#!/bin/sh
su pi -l -c "nohup python3 /home/pi/test.py > /home/pi/test.log &"
