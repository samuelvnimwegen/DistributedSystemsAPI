"""
Database configuration
"""
from flask_sqlalchemy import SQLAlchemy
from src.database.base import Base

db = SQLAlchemy(model_class=Base,
                engine_options={
                    "pool_pre_ping": True,
                    "pool_recycle": 300,
                    "pool_size": 10,
                    "max_overflow": 20,
                    "isolation_level": "READ COMMITTED"
                })
