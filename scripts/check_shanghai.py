#!/usr/bin/env python3
"""Verify compiled src/ bytecode contains no Cancun-only EVM opcodes (Aevum requires Shanghai)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

CANCUN_OPCODES: dict[int, str] = {
    0x49: "BLOBHASH",
    0x4A: "BLOBBASEFEE",
    0x5C: "TLOAD",
    0x5D: "TSTORE",
    0x5E: "MCOPY",
}


def find_cancun_opcodes(hex_bytecode: str) -> list[str]:
    """Scan EVM bytecode skipping PUSH immediate data and trailing CBOR metadata."""
    raw = hex_bytecode.removeprefix("0x").strip()
    if not raw:
        return []
    code = bytes.fromhex(raw)
    meta_len = int.from_bytes(code[-2:], "big") + 2 if len(code) >= 2 else 0
    end = len(code) - meta_len if 0 < meta_len < len(code) else len(code)

    found: list[str] = []
    i = 0
    while i < end:
        op = code[i]
        if op in CANCUN_OPCODES:
            found.append(f"{CANCUN_OPCODES[op]} at byte {i}")
        if 0x60 <= op <= 0x7F:
            i += op - 0x5F
        i += 1
    return found


def check_out_dir(out_dir: Path) -> int:
    checked = 0
    failed = 0
    for json_path in sorted(out_dir.rglob("*.json")):
        data = json.loads(json_path.read_text(encoding="utf-8"))
        meta = data.get("metadata")
        if isinstance(meta, str):
            meta = json.loads(meta)
        if not isinstance(meta, dict):
            continue
        targets = meta.get("settings", {}).get("compilationTarget", {})
        if not any(str(k).startswith("src/") for k in targets):
            continue
        source_name = next(iter(targets.keys()), json_path.name)
        for kind, key in (("runtime", "deployedBytecode"), ("creation", "bytecode")):
            hex_obj = (data.get(key) or {}).get("object", "")
            if not hex_obj or hex_obj == "0x":
                continue
            checked += 1
            bad = find_cancun_opcodes(hex_obj)
            if bad:
                failed += 1
                print(f"FAIL {source_name} ({kind}): {', '.join(bad)}", file=sys.stderr)
    if checked == 0:
        print(f"No compiled src/ artifacts found in {out_dir}. Run forge build first.", file=sys.stderr)
        return 1
    if failed:
        print("Set evm_version = 'shanghai' in foundry.toml.", file=sys.stderr)
        return 1
    print(f"OK: {checked} bytecode blobs verified Shanghai-safe.")
    return 0


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("out")
    raise SystemExit(check_out_dir(target))
