#!/bin/sh
su pi -l -c "nohup python3 /home/pi/vibtest/test.py > /home/pi/vibtest/vibtest.log &"
