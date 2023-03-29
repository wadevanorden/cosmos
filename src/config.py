import os

SECRET_KEY = os.getenv('SECRET_KEY')
MYSQL_HOST = 'aurora-mysql-cosmos-dev.cluster-cku0taepgyyj.us-east-1.rds.amazonaws.com'
MYSQL_USER = 'admin'
MYSQL_PASSWORD = os.getenv('MYSQL_DEV_PASSWORD')
MYSQL_DB = 'achievements_main_dev'