"""Raw store inmutable + estado de cursores (SQLite stdlib, cero dependencias).

Da tres garantías del diseño (docs/05):
  - Crudo inmutable: guarda el payload tal cual (re-procesable si mejora el motor).
  - Idempotencia: (source, external_id) no se duplica; mismo hash = sin cambio.
  - Incremental: cada fuente guarda su cursor para no re-traer todo.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from typing import Iterable, Optional

from .source import RawRecord, utcnow_iso


@dataclass
class UpsertResult:
    status: str   # "new" | "changed" | "unchanged"


class RawStore:
    def __init__(self, path: str = ":memory:"):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS raw_records (
                source        TEXT NOT NULL,
                external_id   TEXT NOT NULL,
                record_type   TEXT NOT NULL,
                hash          TEXT NOT NULL,
                fetched_at    TEXT NOT NULL,
                payload_json  TEXT NOT NULL,
                PRIMARY KEY (source, external_id)
            );
            CREATE TABLE IF NOT EXISTS source_state (
                source      TEXT PRIMARY KEY,
                cursor      TEXT,
                updated_at  TEXT NOT NULL
            );
            """
        )
        self.conn.commit()

    def upsert(self, rec: RawRecord) -> UpsertResult:
        cur = self.conn.execute(
            "SELECT hash FROM raw_records WHERE source=? AND external_id=?",
            (rec.source, rec.external_id),
        )
        row = cur.fetchone()
        if row is None:
            status = "new"
        elif row["hash"] == rec.hash:
            return UpsertResult("unchanged")   # idempotencia: no reescribe
        else:
            status = "changed"                 # el anuncio cambió (p.ej. precio)

        self.conn.execute(
            """INSERT INTO raw_records (source, external_id, record_type, hash, fetched_at, payload_json)
               VALUES (?,?,?,?,?,?)
               ON CONFLICT(source, external_id) DO UPDATE SET
                 record_type=excluded.record_type, hash=excluded.hash,
                 fetched_at=excluded.fetched_at, payload_json=excluded.payload_json""",
            (rec.source, rec.external_id, rec.record_type, rec.hash,
             rec.fetched_at, json.dumps(rec.payload, ensure_ascii=False, default=str)),
        )
        self.conn.commit()
        return UpsertResult(status)

    def get_cursor(self, source: str) -> Optional[str]:
        row = self.conn.execute(
            "SELECT cursor FROM source_state WHERE source=?", (source,)
        ).fetchone()
        return row["cursor"] if row else None

    def set_cursor(self, source: str, cursor: Optional[str]) -> None:
        self.conn.execute(
            """INSERT INTO source_state (source, cursor, updated_at) VALUES (?,?,?)
               ON CONFLICT(source) DO UPDATE SET cursor=excluded.cursor, updated_at=excluded.updated_at""",
            (source, cursor, utcnow_iso()),
        )
        self.conn.commit()

    def records(self, record_type: Optional[str] = None) -> Iterable[dict]:
        q = "SELECT * FROM raw_records"
        params: tuple = ()
        if record_type:
            q += " WHERE record_type=?"
            params = (record_type,)
        for row in self.conn.execute(q, params):
            d = dict(row)
            d["payload"] = json.loads(d.pop("payload_json"))
            yield d

    def count(self, record_type: Optional[str] = None) -> int:
        q = "SELECT COUNT(*) AS n FROM raw_records"
        params: tuple = ()
        if record_type:
            q += " WHERE record_type=?"
            params = (record_type,)
        return self.conn.execute(q, params).fetchone()["n"]

    def close(self) -> None:
        self.conn.close()
