import os
DEBUG = True
LOGGING_CONFIG = "config/logging/prod.conf"
PORT = 5000
APP_NAME = "recipe-recommender"
SQLALCHEMY_TRACK_MODIFICATIONS = True
HOST = "0.0.0.0"
SQLALCHEMY_ECHO = False  # If true, SQL for queries made will be printed
MAX_ROWS_SHOW = 100

# data path
S3_PATHS = ['s3://2021-msia423-chen-zhiyang/raw_data/RAW_recipes.csv',
            's3://2021-msia423-chen-zhiyang/raw_data/RAW_interactions.csv']
LOCAL_RAW_PATHS = ['data/raw/RAW_recipes.csv', 'data/raw/RAW_interactions.csv']
RDS_DATA_PATH = 'data/clean/rds.csv'
MODEL_DATA_PATH = 'model/kmeans.pkl'

# Connection string
DB_HOST = os.environ.get('MYSQL_HOST')
DB_PORT = os.environ.get('MYSQL_PORT')
DB_USER = os.environ.get('MYSQL_USER')
DB_PW = os.environ.get('MYSQL_PASSWORD')
DATABASE = os.environ.get('DATABASE_NAME')
DB_DIALECT = 'mysql+pymysql'
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')
if SQLALCHEMY_DATABASE_URI is not None:
    pass
elif DB_HOST is None:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///data/recipe.db'
else:
    SQLALCHEMY_DATABASE_URI = f'{DB_DIALECT}://{DB_USER}:{DB_PW}@{DB_HOST}:{DB_PORT}/{DATABASE}'
