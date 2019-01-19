## when upgrading mysql each time, need to upgrade in case of error
## mysql -u root -p
## mysql > SET GLOBAL innodb_fast_shutdown = 1;
## mysql_upgrade -u root -p

mysql -u root -p "telegram" < schema.sql
mysql -u root -p "telegram" < insert_info.sql