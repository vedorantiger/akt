# config/__init__.py
"""Пакет конфігурації для Fitness CRM"""

from . import config
from .logger import fitness_logger, get_app_logger, get_ui_logger, get_db_logger, get_api_logger
from .database import engine, get_session, init_db

__all__ = [
    'config',
    'fitness_logger',
    'get_app_logger',
    'get_ui_logger', 
    'get_db_logger',
    'get_api_logger',
    'engine',
    'get_session', 
    'init_db'
]
