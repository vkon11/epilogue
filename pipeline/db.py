import os
import time
from pathlib import Path

import truststore
from dotenv import load_dotenv
from supabase import create_client

# Verify HTTPS against the OS certificate store (Python's bundled store fails on this machine).
truststore.inject_into_ssl()
load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def retry(fn, attempts=3):
    """Call fn(), retrying on dropped connections (this network drops them often)."""
    for i in range(attempts):
        try:
            return fn()
        except Exception:
            if i == attempts - 1:
                raise
            time.sleep(2 * (i + 1))


def client():
    """Supabase client with the secret key. Bypasses row-level security, so pipeline only."""
    return create_client(os.environ["NEXT_PUBLIC_SUPABASE_URL"], os.environ["SUPABASE_SECRET_KEY"])
