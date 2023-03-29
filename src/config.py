import os

SECRET_KEY = os.getenv('secret-key')
MYSQL_HOST = 'aurora-mysql-cosmos-dev.cluster-cku0taepgyyj.us-east-1.rds.amazonaws.com'
MYSQL_USER = 'admin'
MYSQL_PASSWORD = os.getenv('mysql-dev-password')
MYSQL_DB = 'achievements_main_dev'