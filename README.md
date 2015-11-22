# DockerDNS

DockerDNS is a little dns server, which populate containers ip by their names thought dns. This 
solve problems with random generated ip's of the docker container and gives possibility to serve the application
to the external world.


# How To Use

DockerDNS could be used in various ways, just like any other dns server, except on;y one thing:
  - DockerDNS is only authoritative server, not recursive request
  - DockerDNS supports only A and PTR requests, while PRT used only to resolve his ip
  
DockerDNS could be perfectly used for reverse proxying docker container http port via nginx, for example:
 - we have some container called **"example1"** with available port **80**
 - this container sitting on docker bridge with some permissions and we doesn't want to link this port to us real interfaces.
 
 Forwarding will not help, coz after every container restart, container ip will be changes. And we have several options:
 - tune static ip for container via workarounds
 - use dockerDNS
 
 All options will help, however second one not require any special tuning or magic with container, as result is more easy and can be configured more faster
 
# Requirements
 - python 3
 - docker-py (can be installed via pip)
 
# How To Install
  - git clone https://github.com/hapylestat/dockerDNS.git
  - adjust settings in *conf/main.json* (doker.url option supports tcp and unix sockets)
  - now you need just run server: *python3 doker_dns.py*
  
# Install as system service, systemd example:
- create **dockerdns.service** file:
```
[Unit]
Description=docker dns service
After=syslog.target network-online.target
Requires=docker.service

[Service]
Type=simple
ExecStart=/usr/bin/python3 /usr/srv/dockerDNS/docker_dns.py
ExecStop=/bin/kill -s QUIT $MAINPID
User=root
Group=root
PermissionsStartOnly=true

[Install]
WantedBy=multi-user.target
```
- systemctl daemon-reload
- systemctl enable dockerdns
- systemctl start dockerdns 