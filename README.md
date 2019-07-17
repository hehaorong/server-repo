树莓派3B配置过程(rasbian-buster版本):

1. raspi-config:
设置键盘布局(general 101 key-> US)
设置区域(locale)和时区
设置SSH使能
修改hostname为haorongMango

2.
设置locale
dpkg-reconfigure locales  (ZH_cn.UTF-8作为默认)

修改pi的用户、组名称为embed
usermod -l embed pi    
groupmod -n embed pi


3. 安装基本包
$ apt-get install vim vstfp nethogs htop hdparm redis redis-sentinel
$ apt-get install mariadb-server mariadb-client
$ apt-get install nginx php7.1 git
$ apt-get install python-pip python3.7-pip

$ apt-get install ufw git chkconfig supervisor


执行以下命令:

设置防火墙允许端口
$ ufw limit 22
$ ufw allow 20:21/tcp
$ ufw allow 80
$ ufw allow 443
$ ufw allow 3306
$ ufw allow 9900:10000/tcp
$ ufw allow 9900:10000/udp
$ ufw allow 9000

$ ufw enable
$ mkdir /media/ext4 /media/ntfs
$ adduser git   # 创建git用户


4. 安装acme.sh(let's encrypt)

以下命令下载acme: https://github.com/Neilpang/acme.sh/archive/master.tar.gz
安装到/root/.acme.sh目录

$ curl https://get.acme.sh | sh 
$ cp /root/.acme.sh /opt  /opt/acme -rp

$ vim /root/.bashrc              <- 删除最后一行:  . "/root/.acme.sh/acme.sh.env"
$ vim /opt/.acme.sh/acme.sh.env  <- 修改内容: LE_WORKING_DIR="/tmp/.acme.sh"  acme.sh="/opt/.acme.sh/acme.sh"

禁止history
$ vim /etc/profile               <- 末尾添加, 禁止history命令 export HISTSIZE=0
$ vim /home/embed/.bashrc        <- HISTSIZE=1000, HISTFILESIZE=2000屏蔽掉


5. 将配置文件拷贝到对应位置
以仓库(https://github.com/hehaorong/server-repo)的配置文件为模板, 修改本地的配置文件




6.安装gateone、gogs、owncloud、wordpress
/usr/local/bin/sys-init.sh || echo "" > /dev/null

gateone
mount -t ext4 /dev/sd-sandisk /media/ext4
mount -t tmpfs -o size=200m tmpfs /media/ext4/ftp/temp

#ntfs-3g -o uid=33,gid=33,umask=0007 /dev/sda1 /media/ntfs
mount -t ntfs  /dev/sd-toshiba  /media/ntfs

pip3 install flask flask-sqlalchemy flask-wtf flask-login flask-debugtoolbar bootstrap-flask  flask-babel flask-socketio
pip3 install click redis python-dotenv pyserial mysqlclient kombu pika jieba imageio gevent gevent-websocket flower
pip3 install flask-whooshee flask-restplus flask-moment flask-migrate flask-dropzone flask-cors flask-caching flask-ckeditor
pip3 install flask-babel flask-avatars flask-assets faker crypto coverage beach  flask-oauthlib moviepy httpie imageio-ffmpeg
pip3 install gunicorn uwsgi flask-mail flask-limiter flask-jwt 
5. acme

