from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import sqlite3
from typing import Any


@dataclass(frozen=True)
class RepairObservation:
    raw_text: str
    repaired_text: str
    used_fallback: bool
    error: str = ""
    profile: str = "default"
    model: str = ""
    assets_dir: str = ""


def default_database_path() -> Path:
    return Path.home() / ".local" / "share" / "voxtype-post-processing" / "history.sqlite3"


def connect(path: str | Path | None = None) -> sqlite3.Connection:
    db_path = Path(path) if path is not None else default_database_path()
    db_path = db_path.expanduser()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL")
    migrate(conn)
    return conn


def migrate(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS repair_observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            observed_at TEXT NOT NULL,
            raw_text TEXT NOT NULL,
            repaired_text TEXT NOT NULL,
            used_fallback INTEGER NOT NULL,
            error TEXT NOT NULL DEFAULT '',
            profile TEXT NOT NULL DEFAULT 'default',
            model TEXT NOT NULL DEFAULT '',
            assets_dir TEXT NOT NULL DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS correction_candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            raw_phrase TEXT NOT NULL,
            proposed_repair TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'unspecified',
            reason TEXT NOT NULL DEFAULT '',
            example_observation_id INTEGER,
            frequency INTEGER NOT NULL DEFAULT 1,
            status TEXT NOT NULL DEFAULT 'pending',
            FOREIGN KEY(example_observation_id) REFERENCES repair_observations(id)
        );
        """
    )
    conn.commit()


def record_observation(conn: sqlite3.Connection, observation: RepairObservation) -> int:
    cursor = conn.execute(
        """
        INSERT INTO repair_observations (
            observed_at, raw_text, repaired_text, used_fallback, error, profile, model, assets_dir
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now(timezone.utc).isoformat(),
            observation.raw_text,
            observation.repaired_text,
            int(observation.used_fallback),
            observation.error,
            observation.profile,
            observation.model,
            observation.assets_dir,
        ),
    )
    conn.commit()
    return int(cursor.lastrowid)


def rows(conn: sqlite3.Connection, query: str, params: tuple[Any, ...] = ()) -> list[sqlite3.Row]:
    conn.row_factory = sqlite3.Row
    return list(conn.execute(query, params))
