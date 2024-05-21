#!/bin/bash
# git clone https://github.com/jaydoncheng/smsensor-proxy-server.git
git pull
screen -S smsensor-proxy-server -X quit
screen -dmS smsensor-proxy-server
screen -S smsensor-proxy-server -X 'gunicorn :80 --workers 2 --threads 32 app:app'
