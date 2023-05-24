import os
from dotenv import load_dotenv
from pathlib import Path


class SystemConfig:
    root_dir = Path(__file__).resolve().parents[1]
    dotenv_path = Path(root_dir).joinpath('.env')
    load_dotenv(dotenv_path)

    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{user}:{password}@{host}/{db_name}?charset=utf8'.format(**{
        'user': os.environ.get('DB_USER'),
        'password': os.environ.get('DB_PASS'),
        'host': os.environ.get('DB_HOST'),
        'db_name': os.environ.get('DB_NAME'),
    })

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False


config = SystemConfig
