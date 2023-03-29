import os

SECRET_KEY = os.getenv('secret-key')
MYSQL_HOST = 'aurora-mysql-achievements-dev-instance-1.cku0taepgyyj.us-east-1.rds.amazonaws.com'
MYSQL_USER = 'admin'
MYSQL_PASSWORD = os.getenv('mysql-dev-password')
MYSQL_DB = 'achievements_main_dev'