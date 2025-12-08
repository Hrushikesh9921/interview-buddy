#!/usr/bin/env python
"""Check sessions in database."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import get_db_context, Session

with get_db_context() as db:
    sessions = db.query(Session).all()
    print(f"Total sessions: {len(sessions)}")
    for session in sessions:
        print(f"  - {session.id}: {session.candidate_name} ({session.status.value})")

