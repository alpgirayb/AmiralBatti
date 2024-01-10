import os


class LocalBaseConfig:
    """
       The base config that all other configs inherit from.
       General settings are set here.
       """
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@127.0.0.1/game"
    SQLALCHEMY_TRACK_MODIFICATIONS = False