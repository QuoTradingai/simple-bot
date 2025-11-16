"""Upload local RL experiences to the cloud /api/ml/save_experience endpoint."""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List, Optional

import requests

DEFAULT_URL = (
    "https://quotrading-signals.icymeadow-86b2969e.eastus.azurecontainerapps.io"
    "/api/ml/save_experience"
)
DEFAULT_SIGNAL_PATH = Path("data/local_experiences/signal_experiences_v2.json")
DEFAULT_EXIT_PATH = Path("data/local_experiences/exit_experiences_v2.json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default=DEFAULT_URL, help="Cloud API endpoint")
    parser.add_argument("--user-id", default="local_sync", help="user_id stored in cloud")
    parser.add_argument("--symbol", default="ES", help="Symbol to associate with payloads")
    parser.add_argument("--start", type=int, default=0, help="Default index offset for uploads")
    parser.add_argument("--limit", type=int, help="Default max records to upload")
    parser.add_argument("--signal-start", type=int, help="Override start for signal data")
    parser.add_argument("--signal-limit", type=int, help="Override limit for signal data")
    parser.add_argument("--exit-start", type=int, help="Override start for exit data")
    parser.add_argument("--exit-limit", type=int, help="Override limit for exit data")
    parser.add_argument("--chunk-size", type=int, default=250, help="Progress output interval")
    parser.add_argument("--sleep", type=float, default=0.0, help="Delay between requests (seconds)")
    parser.add_argument("--timeout", type=float, default=15.0, help="HTTP timeout in seconds")
    parser.add_argument("--retries", type=int, default=3, help="Retries per experience on failure")
    parser.add_argument("--type", choices=["signal", "exit", "both"], default="both",
                        help="Dataset(s) to upload")
    parser.add_argument("--dry-run", action="store_true",
                        help="Build payloads without sending them")
    parser.add_argument("--signal-path", type=Path, default=DEFAULT_SIGNAL_PATH,
                        help="Path to signal_experiences JSON")
    parser.add_argument("--exit-path", type=Path, default=DEFAULT_EXIT_PATH,
                        help="Path to exit_experiences JSON")
    return parser.parse_args()


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def load_experiences(path: Path) -> List[dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Missing experience file: {path}")
    with path.open("r", encoding="utf-8") as fh:
        payload = json.load(fh)
    experiences = payload.get("experiences", [])
    print(f"Loaded {len(experiences):,} rows from {path}")
    return experiences


def derive_quality_score(experience: dict[str, Any], exp_type: str) -> float:
    if exp_type == "signal":
        return clamp(float(experience.get("confidence", 0.5)))
    outcome = experience.get("outcome", {})
    if isinstance(experience.get("quality_score"), (int, float)):
        return clamp(float(experience["quality_score"]))
    if isinstance(outcome.get("entry_confidence"), (int, float)):
        return clamp(float(outcome["entry_confidence"]))
    if isinstance(outcome.get("win"), bool):
        return 1.0 if outcome["win"] else 0.0
    return 1.0


def build_payload(experience: dict[str, Any], exp_type: str, user_id: str, symbol: str) -> dict[str, Any]:
    timestamp = experience.get("timestamp")
    if not timestamp:
        timestamp = datetime.now(timezone.utc).isoformat()
    payload = {
        "user_id": user_id,
        "symbol": experience.get("symbol", symbol),
        "experience_type": exp_type,
        "rl_state": experience,
        "outcome": experience.get("outcome", {}),
        "quality_score": derive_quality_score(experience, exp_type),
        "timestamp": timestamp,
    }
    if exp_type == "signal":
        payload["outcome"] = {
            "pnl": experience.get("pnl", 0.0),
            "outcome": experience.get("outcome", "UNKNOWN"),
            "took_trade": experience.get("took_trade", False),
            "confidence": experience.get("confidence"),
        }
    return payload


def post_with_retries(session: requests.Session, url: str, payload: dict, timeout: float,
                      retries: int) -> bool:
    for attempt in range(1, retries + 1):
        try:
            response = session.post(url, json=payload, timeout=timeout)
            if response.ok:
                return True
            message = f"{response.status_code} - {response.text[:200]}"
        except requests.RequestException as exc:
            message = str(exc)
        if attempt == retries:
            print(f"  ❌ Failed after {retries} attempts: {message}")
            return False
        wait_for = min(2 ** attempt, 10)
        print(f"  ⚠️  Attempt {attempt} failed ({message}). Retrying in {wait_for}s...")
        time.sleep(wait_for)
    return False


def sync_dataset(experiences: List[dict[str, Any]], exp_type: str, *, start: int,
                 limit: Optional[int], args: argparse.Namespace,
                 session: requests.Session) -> int:
    if not experiences:
        return 0
    start = max(start, 0)
    end = len(experiences) if limit is None else min(len(experiences), start + max(limit, 0))
    if start >= end:
        print(f"No {exp_type} experiences selected (start={start}, end={end}).")
        return 0
    subset = experiences[start:end]
    progress_interval = args.chunk_size if args.chunk_size and args.chunk_size > 0 else len(subset)
    print(f"Uploading {len(subset):,} {exp_type} experiences (idx {start} to {end - 1})...")
    uploaded = 0
    for offset, exp in enumerate(subset, start=1):
        payload = build_payload(exp, exp_type, args.user_id, args.symbol)
        if args.dry_run:
            if offset == 1:
                preview = json.dumps(payload, indent=2)[:500]
                print(f"  DRY RUN preview ({exp_type}):\n{preview}\n  ...")
            uploaded += 1
        else:
            ok = post_with_retries(session, args.url, payload, args.timeout, args.retries)
            if not ok:
                print(f"Stopped at {exp_type} index {start + offset - 1}")
                return uploaded
            uploaded += 1
            if args.sleep:
                time.sleep(args.sleep)
        if uploaded % progress_interval == 0 or offset == len(subset):
            print(f"  ✓ {uploaded}/{len(subset)} {exp_type} experiences uploaded")
    return uploaded


def upload_experiences() -> None:
    args = parse_args()
    session = requests.Session()
    total_uploaded = 0
    try:
        if args.type in {"signal", "both"}:
            signal_data = load_experiences(args.signal_path)
            start = args.signal_start if args.signal_start is not None else args.start
            limit = args.signal_limit if args.signal_limit is not None else args.limit
            total_uploaded += sync_dataset(signal_data, "signal", start=start, limit=limit,
                                           args=args, session=session)
        if args.type in {"exit", "both"}:
            exit_data = load_experiences(args.exit_path)
            start = args.exit_start if args.exit_start is not None else args.start
            limit = args.exit_limit if args.exit_limit is not None else args.limit
            total_uploaded += sync_dataset(exit_data, "exit", start=start, limit=limit,
                                           args=args, session=session)
    finally:
        session.close()
    action = "simulated" if args.dry_run else "uploaded"
    print(f"\n✅ {action.capitalize()} {total_uploaded:,} experiences total")


if __name__ == "__main__":
    try:
        upload_experiences()
    except KeyboardInterrupt:
        sys.exit("Interrupted by user")
