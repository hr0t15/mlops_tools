#!/bin/bash
ETH_DEV=enp3s0
HOST_IP=`ip -f inet -o addr show ${ETH_DEV} |cut -d\  -f 7 | cut -d/ -f 1`

cat << EOF
# DBの設定値
DB_HOST=tracking-db
DB_NAME=mlflowdb
POSTGRES_USER=postgres
POSTGRES_PASSWORD=mlflow123

# pgadminの設定値
PGADMIN_EMAIL=mlflow@test.info
PGADMIN_PASSWORD=mlflow123

# pure-ftpdの設定値
HOST_IP=${HOST_IP}
FTP_USER_NAME=mlflow_ftp
FTP_USER_PASS=mlflow123
EOF
