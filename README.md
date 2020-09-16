# py-cloudflare-dns-updater

A simple python program that keeps your dns record pointing to your public ip address.

- [py-cloudflare-dns-updater](#py-cloudflare-dns-updater)
  - [Requirements](#requirements)
  - [How to setup](#how-to-setup)
  - [Running using docker and docker-compose](#running-using-docker-and-docker-compose)
  - [Running using python](#running-using-python)

## Requirements

-   Python 3.7 or latest

or

-   docker
-   docker-compose

## How to setup

It's all environment variables based.

- Create a file called .env

- Copy the content of .env.example to your .env and edit according to your need
  
- Your .env should look like this:
```bash
# DNS subdomain record to be updated
CF_RECORD=subdomain.domain.com
# Self explanatory
CF_ZONE=domain.com
# Set False if you don't want enable trafic through cloudflare for this dns record, True if you want
# Default will be True
CF_RECORD_PROXIED=
# Set custom ttl time (seconds)
# Default will be 1
CF_RECORD_TTL=
# Your cloudflare account email
CF_AUTH_EMAIL=bolinha@email.com
# Your cloudflare api key
# See how to get yours bellow
# https://support.cloudflare.com/hc/en-us/articles/200167836-Where-do-I-find-my-Cloudflare-API-key-
CF_AUTH_KEY=laksjdhwbasncmodasjxcn

# Time (seconds) between each ip change verification
# Default will be 3600
TIME_INTERVAL=30

# Set anything if you want to enable debugging logs, or leave it empty if you don't want to.
DEBUG=

```

## Running using docker and docker-compose

Just use this command
```
docker-compose up -d
```

if you want to see logs

```
docker logs dns-updater --follow
```

## Running using python

If you not gonna use docker, install the dependencies with following command
```
pip3 install -r requirements.txt
```

after that...

```
python3 updater.py
```