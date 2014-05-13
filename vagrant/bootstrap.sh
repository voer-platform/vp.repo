#!/usr/bin/env bash
apt-get update -y
apt-get install -y git python-virtualenv python-dev python-software-properties

apt-key adv --recv-keys --keyserver keyserver.ubuntu.com 0xcbcb082a1bb943db
add-apt-repository 'deb http://download.nus.edu.sg/mirror/mariadb/repo/5.5/debian wheezy main'
apt-get update -y
export DEBIAN_FRONTEND=noninteractive
debconf-set-selections <<< 'mariadb-server-5.5 mysql-server/root_password password'
debconf-set-selections <<< 'mariadb-server-5.5 mysql-server/root_password_again password'
apt-get install -y mariadb-server mariadb-client libmariadbclient-dev
#/etc/init.d/mysql start

mysql -u root -e "create database vpr;"
mysql -u root -e "grant all privileges on vpr.* to 'vpr'@'localhost' identified by 'vpr';"
mysql -u root -e "flush privileges;"

su - vagrant
virtualenv vpr
cd vpr
source bin/activate
git clone https://github.com/voer-platform/vp.repo.git
cd vp.repo
sh install.sh
mysql vpr -uvpr -pvpr -e "INSERT INTO django_site (domain, name) VALUES ('localhost', 'localhost');"

chown vagrant.vagrant -R /home/vagrant/vpr

cd vpr
python manage.py runserver 0:2013 &
