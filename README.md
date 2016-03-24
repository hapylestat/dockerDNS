# DockerDNS  

![LGPLv3][logo]

DockerDNS is a little dns server, which populate containers ip by their names thought dns. This 
solve problems with random generated ip's of the docker container and gives possibility to serve the application
to the external world.

# Requirements
 - python 3
 - docker-py (can be installed via pip)
 
# How To Install
  - git clone https://github.com/hapylestat/dockerDNS.git
  - adjust settings in *conf/main.json* (doker.url option supports tcp and unix sockets)
  - now you need just run server: *python3 doker_dns.py*

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

# Nginx configuration sample (reverse proxy)
```
server {
    listen       127.0.0.1:80;
    server_name  my.docker.server;

    #  where 127.0.0.3 is an address of dockerDNS
    resolver 127.0.0.3 ipv6=off;
    set $upstream "http://container-name:80";


    location / {
        proxy_pass          $upstream;
        proxy_http_version  1.1;
        proxy_set_header    X-Forwarded-For $remote_addr;
        proxy_set_header    Host $server_name:$server_port;
    }
}
```
 
 
# Install as system service, systemd example:
- create **dockerdns.service** file:
```
[Unit]
Description=docker dns service
After=syslog.target network-online.target
Requires=docker.service

[Service]
Type=simple
ExecStart=/usr/bin/python3 /path/to/server/docker_dns.py
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

# Integration with BIND

Zone configuration:
```
zone "docker.zone" IN {
  type forward;
  forwarders { 127.0.0.3; };
};
```
Reverse zone:
```
zone "10.168.192.in-addr.arpa" IN {
  type forward;
  forwarders { 127.0.0.3; };
};
```

Where docker.zone is your docker domain name, 192.168.10.0/24 docker address space. To forward reverse queries, BIND require 
"empty-zones-enable no;" in the named.conf settings


[logo]: http://www.gnu.org/graphics/lgplv3-147x51.png
