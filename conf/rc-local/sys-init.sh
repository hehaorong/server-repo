#!/bin/bash

LOG_PATH="/var/log"


# params: is_dir, path, filename, mode, owner, group
# example: create_log_file(0, "/var/log", "ok.log", "0755", "root", "adm")
# description: create log file /var/log/ok.log
_create_file(){

    path="$2/$3"
    echo "path: $path"
    if ! [ -e "$path" ]; then
        if [ "$1" -lt "1" ]; then
            touch "$path"
        else
            mkdir "$path"
        fi
        chmod "$4" -R "$path"
        chown "$5.$6" -R "$path"
    fi
}


# params: dirname, mode, own, group
# example: create_log_dir("nginx", "0755", "root", "pam")
# description: create /var/log/nginx directory
create_log_dir(){
    if [ "$#" -lt 4 ]; then
        echo "error in create_dir_file(): args not valid."
        return 0
    fi
    _create_file 1 $LOG_PATH $* || echo "" > /dev/null
}

# params: filename, mode, own, group
# example: create_log_file("ok.log", "0754", "www-data", "pam")
# description: create log file /var/log/ok.log
create_log_file(){
    if [ "$#" -lt 4 ]; then
        echo "error in create_dir_file(): args not valid."
        return 0
    fi
    _create_file 0 $LOG_PATH $* || echo "" > /dev/null
}



# params: path, dirname, mode, own, group
# example: create_log_file("/tmp", "ftp_temp", "0777", "embed", "embed")
# description: create dir /tmp/ftp_temp
create_dir(){
    if [ "$#" -lt 5 ]; then
        echo "error in create_dir(): args not valid, args: $*."
        return 0
    fi
    _create_file 1 $*   || echo "" > /dev/null
}


# params: path, filename, mode, own, group
# example: create_file("/tmp", "ok.py", "0777", "embed", "embed")
# description: create file /tmp/ok.py
create_file(){
    if [ "$#" -lt 5 ]; then
        echo "error in create_file(): args not valid, args: $*"
    fi
    _create_file 0 $* || echo "" > /dev/null
}


# halt the wlan hardware
ifconfig wlan0 down 

# mount removable harddisk
mount -t ext4 /dev/sd-sandisk /media/ext4
mount -t tmpfs -o size=200m tmpfs /media/ext4/ftp/temp

#ntfs-3g -o uid=33,gid=33,umask=0007 /dev/sda1 /media/ntfs
mount -t ntfs  /dev/sd-toshiba  /media/ntfs

# ftp temp dir
# create_dir "/tmp" "ftp_temp" "0755" "embed" "embed"


# gogs log dir
create_log_dir "gogs" "0755" "git"  "git"


# ssh, hosts.deny, hosts.deny
create_file "/tmp" "hosts.deny" "0777" "root" "root"
create_file "/tmp" "hosts.allow" "0777" "root" "root"


# gunicorn
create_log_dir "gunicorn" "0755" "www-data" "www-data"

# mysql
create_log_dir "mysql" "0755" "mysql" "adm"
create_log_file "mysql/error.log" "0660" "mysql" "adm"

# nginx
create_log_dir "nginx" "0755" "root" "adm"
create_log_file "nginx/access.log" "0640" "www-data" "adm"
create_log_file "nginx/error.log" "0640" "www-data" "adm"


# php7.0
create_log_file "php7.0-fpm.log" "0600" "root" "root"

# redis
create_log_dir "redis" "0750" "redis" "redis"
create_log_file "redis/redis-sentinel.log" "0660" "redis" "redis"
create_log_file "redis/redis-server.log" "0660" "redis" "redis"

# supervisor
create_log_dir "supervisor" "0755" "root" "root"
create_log_file "supervisor/supervisord.log" "0644" "root" "root"


exit 0
