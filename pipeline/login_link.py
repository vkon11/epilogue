"""Print a one-time login link without sending an email (skips Supabase's email rate limit).
Usage: pipeline/.venv/Scripts/python pipeline/login_link.py [base_url]"""
import sys

from db import client

EMAIL = "vskondur@umich.edu"
base = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3000"

link = client().auth.admin.generate_link({"type": "magiclink", "email": EMAIL})
print(f"{base}/auth/confirm?token_hash={link.properties.hashed_token}&type=magiclink")
