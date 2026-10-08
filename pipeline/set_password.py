"""Set the dashboard login password (no email involved).
Usage: pipeline/.venv/Scripts/python pipeline/set_password.py <password>"""
import sys

from db import client

EMAIL = "vskondur@umich.edu"

admin = client().auth.admin
user = next(u for u in admin.list_users() if u.email == EMAIL)
admin.update_user_by_id(user.id, {"password": sys.argv[1]})
print(f"Password set for {EMAIL}")
