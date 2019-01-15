#!/bin/bash

# touch /tmp/hosts.deny && (rm /etc/hosts.deny or 1) && ln -s /tmp/hosts.deny /etc/hosts.deny    

cat /var/log/auth.log|awk '/Failed/{print $(NF-3)}'|sort|uniq -c|awk '{print $2"="$1;}' > /tmp/black.list
for i in `cat /tmp/black.list`
do
    IP=`echo $i |awk -F= '{print $1}'`
    NUM=`echo $i|awk -F= '{print $2}'`
    if [ ${NUM} -ge 3 ];then
        #echo "ip:"$IP", num: "$NUM
        grep $IP /etc/hosts.deny > /dev/null
        if [ $? -gt 0 ]; then
            echo "sshd:$IP:deny" >> /etc/hosts.deny
        fi
    fi
done

