#!/bin/bash
# git clone https://github.com/jaydoncheng/smsensor-proxy-server.git
git pull
gunicorn -b :80 --workers 2 --threads 32 app:app
