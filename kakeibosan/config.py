import os


class DevelopmentConfig:
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' \
                              + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'models/kakeibosan.db')
    SECRET_KEY = '\xec\x0e\x0f\x87\x83I\x87\x0b\xef\xfb\x15\xb8\xeb\xeb\x1e\x87M'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False


config = DevelopmentConfig
