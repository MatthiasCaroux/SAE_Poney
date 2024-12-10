from .app import app
from .app import mysql 
from .app import login_manager
import app.views
import app.models
import app.commands

def create_app():
    return app