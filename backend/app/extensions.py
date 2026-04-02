import bcrypt

if not hasattr(bcrypt, "__about__"):
    bcrypt.__about__ = type("About", (object,), {"__version__": bcrypt.__version__})

from flask_sqlalchemy import SQLAlchemy
from flask_security import Security
from flask_caching import Cache
from flask_mail import Mail

db = SQLAlchemy()
security = Security()
cache = Cache()
mail = Mail()
