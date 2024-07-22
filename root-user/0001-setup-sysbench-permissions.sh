#!/bin/bash
mysql -u root -pmy-secret-pw -e "CREATE USER sbtest@'%' IDENTIFIED BY 'password'; GRANT ALL PRIVILEGES ON sbtest.* to sbtest@'%';"
