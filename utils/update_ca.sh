#!/bin/bash


# /etc/crontab添加以下配置   
# *        */24   *       *       *       root    $(/usr/local/bin/update_ca.sh > /dev/null &) || (echo "" >/dev/null)

# 删除历史文件
rm -rf /tmp/acme

# 通过ACME进行DNSPOD验证
export DP_Id="xxxx"                    # ****************自行修改************************
export DP_Key="xxxxxxxxxxxx"           # ****************自行修改************************
export LE_WORKING_DIR="/tmp/acme"


# CA证书在有效期前1天进行更新
if [ -e "/etc/ssl/certs/hehaorong.vip.cer" ];then
    export CA_END_TIME=$(date +%s -d "$(openssl x509 -in /etc/ssl/certs/hehaorong.vip.cer -noout -enddate | awk -F'=' '{print $2}')")
    export CA_UPDATE_TIME=$((CA_END_TIME-24*60*60))
    export CUR_TIME=$(date -d today +%s)
fi


# CA证书不存在或已超期则重新获取证书
if [ ! -f "/etc/ssl/certs/hehaorong.vip.cer" ] || [ "$CUR_TIME" -ge "$CA_UPDATE_TIME" ];then
    
    /opt/acme/acme.sh --issue --force --dns dns_dp -d hehaorong.vip -d *.hehaorong.vip
    
    cp /tmp/acme/hehaorong.vip/hehaorong.vip.cer   /etc/ssl/certs
    cp /tmp/acme/hehaorong.vip/hehaorong.vip.key   /etc/ssl/private

    systemctl restart nginx
fi
