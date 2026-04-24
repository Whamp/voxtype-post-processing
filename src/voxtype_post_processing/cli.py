from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

from voxtype_post_processing.assets import default_assets_dir, load_asset_bundle
from voxtype_post_processing.history import RepairObservation, connect, record_observation
from voxtype_post_processing.llm import OpenAICompatibleClient, OpenAICompatibleConfig
from voxtype_post_processing.repair import RepairRequest, repair_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Repair Voxtype transcriptions for insertion-ready output.")
    parser.add_argument(
        "--assets-dir",
        type=Path,
        default=Path(os.getenv("VOXTYPE_REPAIR_ASSETS", default_assets_dir())),
        help="Directory containing repair asset files.",
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=Path(os.getenv("VOXTYPE_REPAIR_DB", "~/.local/share/voxtype-post-processing/history.sqlite3")).expanduser(),
        help="SQLite database for repair history.",
    )
    parser.add_argument("--no-history", action="store_true", help="Do not record this repair observation.")
    parser.add_argument("--profile", default=os.getenv("VOXTYPE_REPAIR_PROFILE", "default"))
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    raw_text = sys.stdin.read()
    recent_context = os.getenv("VOXTYPE_CONTEXT", "")
    config = OpenAICompatibleConfig.from_env()

    try:
        assets = load_asset_bundle(args.assets_dir)
        result = repair_text(
            RepairRequest(raw_text=raw_text, recent_context=recent_context, profile=args.profile),
            assets=assets,
            llm=OpenAICompatibleClient(config),
            max_tokens=config.max_tokens,
        )
    except Exception as exc:  # noqa: BLE001 - stdout must remain usable by Voxtype.
        print(raw_text, end="")
        print(f"voxtype-post-processing failed before repair: {exc}", file=sys.stderr)
        return 0

    print(result.text, end="")
    if result.used_fallback and result.error:
        print(f"voxtype-post-processing repair fallback: {result.error}", file=sys.stderr)

    if not args.no_history:
        try:
            with connect(args.database) as conn:
                record_observation(
                    conn,
                    RepairObservation(
                        raw_text=raw_text,
                        repaired_text=result.text,
                        used_fallback=result.used_fallback,
                        error=result.error,
                        profile=args.profile,
                        model=config.model,
                        assets_dir=str(args.assets_dir),
                    ),
                )
        except Exception as exc:  # noqa: BLE001 - history must not block live dictation.
            print(f"voxtype-post-processing history write failed: {exc}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
