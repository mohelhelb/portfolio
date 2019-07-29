from os import urandom
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app=Flask("pyapp")

# Config
app.config.update(DEBUG=True,
                  SECRET_KEY=urandom(15),
                  SQLALCHEMY_DATABASE_URI=r"sqlite:///schema.db")

# Database
db=SQLAlchemy(app)

# Encryption
bcrypt=Bcrypt(app)


