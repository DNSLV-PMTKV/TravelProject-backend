from .base import *  # noqa

from config.env import env

DEBUG = False

SECRET_KEY = env("SECRET_KEY")
