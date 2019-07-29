from functools import wraps
from flask import flash, redirect, request, session, url_for

def username_in_path(username, path_):
    """Checks if a username is contained in URL"""
    if username in path_:
        return True
    return False

# Decorator
def access_control(func):
    """Checks user's credentials"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            session["active"]
        except KeyError:
            # Message Flashing
            flash("Access Denied", category="danger")
            return redirect(url_for("login"))
        else:
            assert session["username"], "The session object stored no information on username"
            if username_in_path(session["username"], request.path):
                return func(*args, **kwargs)
            # Message Flashing
            flash("Oops! It looks like you're not allowed to access that page", category="info")
            return redirect(url_for("dashboard", username=session["username"]))
    return wrapper