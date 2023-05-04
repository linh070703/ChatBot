#!/bin/bash
set -x
set -e

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

if [ ! -f ./cloudflare-certbot.ini ]; then
    echo "Please create cloudflare-certbot.ini"
    exit
fi

# check if certbot is installed
if ! [ -x "$(command -v certbot)" ]; then
    echo "Certbot is not installed. Installing..."
    sudo apt install nginx snapd -y
    sudo snap install core; sudo snap refresh core
    sudo snap install --classic certbot
    sudo ln -s /snap/bin/certbot /usr/bin/certbot
    sudo snap set certbot trust-plugin-with-root=ok
    sudo snap install certbot-dns-cloudflare
fi

sudo certbot certonly --dns-cloudflare --dns-cloudflare-credentials \
    ./cloudflare-certbot.ini -d '*.jsclub.me'

mkdir -p certs/jsclub.me
sudo cp -L /etc/letsencrypt/live/jsclub.me/fullchain.pem certs/jsclub.me/
sudo cp -L /etc/letsencrypt/live/jsclub.me/privkey.pem certs/jsclub.me/

sudo chown -R $USER:$USER certs
sudo chmod -R 755 certs

sudo systemctl stop nginx
sudo systemctl disable nginx
