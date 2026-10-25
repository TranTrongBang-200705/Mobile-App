"""Scan EdNet KT1 for reproducible, complete-case PCAT cohorts.

The original EdNet release is linked from https://github.com/riiid/ednet.
This scanner reads the public Parquet mirror in small shards, keeps only
question-presence information, and checks the existing local raw subset
against the mirror. It does not change the active PCAT dataset.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import tempfile
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests


DATASET_API = "https://huggingface.co/api/datasets/mgor/EDNet/tree/main?recursive=true"
RESOLVE_BASE = "https://huggingface.co/datasets/mgor/EDNet/resolve/main/"
ROOT = Path(__file__).resolve().parents[2]
QUESTION_CSV = ROOT / "scratch" / "ednet_sample" / "questions.csv"
OLD_RAW_CSV = ROOT / "pcat" / "data" / "Dense_EdNetTOEIC" / "raw_kt1_subset.csv"
OUTPUT_DIR = ROOT / "scratch" / "ednet_reselection"


def list_shards() -> list[dict]:
    response = requests.get(DATASET_API, timeout=30)
    response.raise_for_status()
    entries = response.json()
    return sorted(
        (item for item in entries if item["path"].startswith("kt1/") and item["path"].endswith(".parquet")),
        key=lambda item: item["path"],
    )


def download_shard(entry: dict, path: Path) -> str:
    expected_size = int(entry["size"])
    if path.exists() and path.stat().st_size == expected_size:
        print(f"Using cached {path.name}", flush=True)
    else:
        partial = path.with_suffix(".partial")
        for attempt in range(3):
            try:
                with requests.get(RESOLVE_BASE + entry["path"], stream=True, timeout=120) as response:
                    response.raise_for_status()
                    with partial.open("wb") as output:
                        for chunk in response.iter_content(chunk_size=4 * 1024 * 1024):
                            if chunk:
                                output.write(chunk)
                if partial.stat().st_size != expected_size:
                    raise ValueError(f"Incomplete download: {partial.stat().st_size} != {expected_size}")
                partial.replace(path)
                break
            except (requests.RequestException, OSError, ValueError):
                if attempt == 2:
                    raise
                time.sleep(2 ** attempt)
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def scan(max_shards: int | None = None) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    metadata = pd.read_csv(QUESTION_CSV, usecols=["question_id", "part"])
    q_number = metadata["question_id"].str[1:].astype(int).to_numpy()
    part_by_q = np.zeros(int(q_number.max()) + 1, dtype=np.uint8)
    part_by_q[q_number] = metadata["part"].to_numpy(dtype=np.uint8)

    old_raw = pd.read_csv(OLD_RAW_CSV)
    old_subjects = set(old_raw["subject_id"])
    old_qids = set(old_raw["question_id"].str[1:].astype(int))
    expected_raw = {
        (str(row.subject_id), int(row.timestamp), str(row.question_id)):
        (str(row.user_answer), int(row.solving_id), int(row.elapsed_time))
        for row in old_raw.itertuples(index=False)
    }
    matched_raw = set()
    mismatched_raw = []

    schema = pa.schema(
        [("subject_id", pa.string()), ("items", pa.list_(pa.uint16())),
         ("n_unique", pa.uint16()), ("old_bank_overlap", pa.uint8())]
        + [(f"part_{i}", pa.uint16()) for i in range(1, 8)]
    )
    output_path = OUTPUT_DIR / "user_question_sets.parquet"
    writer = pq.ParquetWriter(output_path, schema=schema, compression="zstd")
    buffer = {name: [] for name in schema.names}
    scanned_rows = 0
    scanned_users = 0
    repeats = 0
    old_bank_full_users = 0
    unknown_question_rows = 0
    shard_results = []
    pending_subject = None
    pending_items: list[str] = []

    def flush_buffer() -> None:
        if buffer["subject_id"]:
            writer.write_table(pa.Table.from_pydict(buffer, schema=schema))
            for values in buffer.values():
                values.clear()

    def consume_user(subject: str, qids: list[str]) -> None:
        nonlocal scanned_users, repeats, old_bank_full_users, unknown_question_rows
        if not qids:
            return
        items = sorted({int(qid[1:]) for qid in qids})
        known = [qid for qid in items if qid < len(part_by_q) and part_by_q[qid] > 0]
        unknown_question_rows += len(items) - len(known)
        if not known:
            return
        parts = np.bincount(part_by_q[known], minlength=8)
        overlap = len(old_qids.intersection(known))
        buffer["subject_id"].append(subject)
        buffer["items"].append(known)
        buffer["n_unique"].append(len(known))
        buffer["old_bank_overlap"].append(overlap)
        for i in range(1, 8):
            buffer[f"part_{i}"].append(int(parts[i]))
        scanned_users += 1
        repeats += len(qids) - len(items)
        old_bank_full_users += overlap == len(old_qids)
        if len(buffer["subject_id"]) >= 5000:
            flush_buffer()

    try:
        entries = list_shards()
        if max_shards is not None:
            entries = entries[:max_shards]
        for shard_index, entry in enumerate(entries):
            started = time.time()
            temp_path = Path(tempfile.gettempdir()) / f"ednet_kt1_{shard_index:05d}.parquet"
            digest = download_shard(entry, temp_path)
            parquet = pq.ParquetFile(temp_path)
            shard_rows = 0
            for batch in parquet.iter_batches(
                batch_size=100_000,
                columns=["subject_id", "question_id", "timestamp", "user_answer", "solving_id", "elapsed_time"],
            ):
                frame = batch.to_pandas()
                sid = frame["subject_id"].to_numpy()
                qid = frame["question_id"].to_numpy()
                shard_rows += len(frame)

                relevant = frame[frame["subject_id"].isin(old_subjects)]
                for row in relevant.itertuples(index=False):
                    key = (str(row.subject_id), int(row.timestamp), str(row.question_id))
                    if key in expected_raw:
                        observed = (str(row.user_answer), int(row.solving_id), int(row.elapsed_time))
                        if observed == expected_raw[key]:
                            matched_raw.add(key)
                        elif len(mismatched_raw) < 20:
                            mismatched_raw.append({"key": key, "expected": expected_raw[key], "observed": observed})

                boundaries = np.flatnonzero(sid[1:] != sid[:-1]) + 1
                starts = np.concatenate(([0], boundaries))
                ends = np.concatenate((boundaries, [len(sid)]))
                for start, end in zip(starts[:-1], ends[:-1]):
                    user = str(sid[start])
                    values = qid[start:end].tolist()
                    if pending_subject is not None:
                        if pending_subject != user:
                            consume_user(pending_subject, pending_items)
                            pending_items = []
                        else:
                            values = pending_items + values
                            pending_items = []
                    consume_user(user, values)
                    pending_subject = None

                last_start = int(starts[-1])
                last_user = str(sid[last_start])
                last_values = qid[last_start:].tolist()
                if pending_subject is None:
                    pending_subject, pending_items = last_user, last_values
                elif pending_subject == last_user:
                    pending_items.extend(last_values)
                else:
                    consume_user(pending_subject, pending_items)
                    pending_subject, pending_items = last_user, last_values

            scanned_rows += shard_rows
            shard_results.append({
                "path": entry["path"], "bytes": int(entry["size"]), "sha256": digest,
                "rows": shard_rows, "seconds": round(time.time() - started, 2),
            })
            print(
                f"Shard {shard_index + 1}/{len(entries)}: {shard_rows:,} rows; "
                f"{scanned_users:,} completed users; {len(matched_raw):,}/{len(expected_raw):,} old rows verified; "
                f"{shard_results[-1]['seconds']:.1f}s",
                flush=True,
            )
            del parquet
            temp_path.unlink()

        if pending_subject is not None:
            consume_user(pending_subject, pending_items)
        flush_buffer()
    finally:
        writer.close()

    manifest = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "source": "https://huggingface.co/datasets/mgor/EDNet",
        "official_release": "https://github.com/riiid/ednet",
        "parquet_mirror_note": "Public third-party mirror; row-level old-subset verification is reported below.",
        "shards": shard_results,
        "rows_scanned": scanned_rows,
        "users_scanned": scanned_users,
        "repeated_question_rows": repeats,
        "unknown_question_count": unknown_question_rows,
        "old_bank_complete_users": old_bank_full_users,
        "existing_raw_rows_matched_exactly": len(matched_raw),
        "existing_raw_rows_total": len(expected_raw),
        "existing_raw_rows_missing": len(expected_raw) - len(matched_raw),
        "existing_raw_mismatches": mismatched_raw,
        "user_question_sets_file": output_path.name,
    }
    (OUTPUT_DIR / "scan_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({key: manifest[key] for key in (
        "rows_scanned", "users_scanned", "old_bank_complete_users",
        "existing_raw_rows_matched_exactly", "existing_raw_rows_missing",
    )}, indent=2), flush=True)


if __name__ == "__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument("scan", choices=["scan"])
    cli.add_argument("--max-shards", type=int, default=None)
    args = cli.parse_args()
    scan(args.max_shards)
