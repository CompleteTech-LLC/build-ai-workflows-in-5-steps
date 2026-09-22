#!/usr/bin/env python3
"""Package this repository's workflow-builder skill, not a user's generated skill."""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import zipfile
from pathlib import Path

sys.dont_write_bytecode = True
if __package__:
    from .validate_quality import FILES, NAME, ROOT, VERSION, validate
    from .validate_skill import no_symlinks
else:
    from validate_quality import FILES, NAME, ROOT, VERSION, validate
    from validate_skill import no_symlinks


def package(destination: Path, root: Path = ROOT) -> dict:
    report = validate(root)
    destination = Path(destination).absolute()
    no_symlinks(destination)
    target, archive = destination / NAME, destination / f"{NAME}.zip"
    for path in (target, archive):
        if path.exists() or path.is_symlink():
            raise FileExistsError(f"Refusing to overwrite {path.name}")
    payload = {relative: (root / relative).read_bytes() for relative in FILES}
    manifest = {"schema_version": 1, "name": NAME, "version": VERSION,
                "files": report["files"], "validation": "structure-only"}
    payload["builder-package.json"] = (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode()
    destination.mkdir(parents=True, exist_ok=True)
    target.mkdir()
    archive_created = False
    try:
        for relative, data in payload.items():
            p = target / relative
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(data)
        validate(target, installed=True)
        with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED) as z:
            archive_created = True
            for relative, data in sorted(payload.items()):
                info = zipfile.ZipInfo(f"{NAME}/{relative}", date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                z.writestr(info, data)
    except Exception:
        shutil.rmtree(target)
        if archive_created:
            archive.unlink(missing_ok=True)
        raise
    return {"directory": str(target), "archive": str(archive), "files": len(payload),
            "installed": False, "published": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(package(args.destination), indent=2))
        return 0
    except (OSError, ValueError, SyntaxError, TypeError) as exc:
        parser.exit(2, f"Builder skill packaging failed: {exc}\n")


if __name__ == "__main__":
    raise SystemExit(main())
