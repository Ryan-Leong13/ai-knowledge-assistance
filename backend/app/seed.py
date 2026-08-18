"""
Seed script - loads all md files from the knowledge base folder
into the database as Document rows.

Run using:
    python -m backend.app.seed
"""

import logging
from pathlib import Path

from backend.app.database import Base, engine, SessionLocal
from backend.app.services import document_func

logging.basicConfig(level = logging.INFO, format = "%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("seed")

KB_dir = Path(__file__).parent / "data" / "knowledge_base"

# Remove the file type from the title name
# For example: "wfh_policy.md" -> "Wfh Policy"
def _title_from_filename(filename: str) -> str:
    stem = filename.replace(".md" , "")
    return stem.replace("_" , " ").title()


def seed():

    # Create table if they does not exist yet
    Base.metadata.create_all(bind = engine)

    db = SessionLocal()

    try:
        existing = document_func.list_doc(db)
        if existing:
            logger.info(
                "Database already contains %d document(s) - skipping seed. "
                "Delete backend/app/data/knowledge_base.db to reseed from scratch.",
                len(existing)
            )
            return

        md_files = sorted(KB_dir.glob("*.md"))

        if not md_files:
            logger.warning("No .md files found in %s", KB_dir)
            return

        for path in md_files:
            content = path.read_text(encoding = "utf-8")
            title = _title_from_filename(path.name)
            document_func.create_doc(db, title = title, content = content)

        logger.info("Seeded %d document(s) from %s", len(md_files), KB_dir)

    finally:
        db.close()

if __name__ == "__main__":
    seed()