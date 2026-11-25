#!/usr/bin/env python3
# SPDX-License-Identifier: MPL-2.0
"""Checks the application entries (apps/<id>.json) and lists the ones to build.

    check_entries.py [--reserved apps.json] [--base <commit>] [--only <id>]

Prints a JSON list for a workflow matrix: every valid entry, or with --base only
those changed since that commit, or with --only that one. Exits 1 with the
reasons when an entry is invalid. --reserved names NBTFoundry.github.io's
apps.json: an id that another repository already ships there (NBTFoundry's own
applications, NBT Manager) is refused, so a community package signed with the
apps key can never update one of them."""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HERE = "NBTFoundry/community-apps"
# NBTFoundry's own sources are never built here, except the examples: the
# pipeline's own test, built and signed like any submitted application.
OWN_ALLOWED = {"NBTFoundry/examples"}
ID = re.compile(r"[a-z0-9_-]{1,48}\Z")
REPO = re.compile(r"[A-Za-z0-9-]{1,39}/[A-Za-z0-9._-]{1,100}\Z")
COMMIT = re.compile(r"[0-9a-f]{40}\Z")
VERSION = re.compile(r"(0|[1-9][0-9]{0,2})\.(0|[1-9][0-9]{0,2})\.(0|[1-9][0-9]{0,2})\Z")
PATH = re.compile(r"[A-Za-z0-9._-]+(/[A-Za-z0-9._-]+)*\Z")
CATEGORIES = {"game", "emulator", "tool", "system"}
TEXT_LIMITS = {"name": 40, "summary": 160, "license": 80}
REQUIRED = {"repository", "commit", "version", "sdk", "build", "payload", *TEXT_LIMITS, "category"}
OPTIONAL = {"package-args": "release/package.args", "lfs": False}


def problems(app, entry, reserved):
    if not ID.fullmatch(app) or app == "manager":
        yield "the file name must be the application id: a-z, 0-9, _ and -, 1 to 48"
    if app in reserved:
        yield f"{app} is already {reserved[app]}'s application"
    if not isinstance(entry, dict):
        yield "not a JSON object"
        return
    missing, unknown = REQUIRED - set(entry), set(entry) - REQUIRED - set(OPTIONAL)
    if missing:
        yield f"missing {sorted(missing)}"
    if unknown:
        yield f"unknown fields {sorted(unknown)}"
    text = lambda key: entry.get(key) if isinstance(entry.get(key), str) else ""
    repository = text("repository")
    if not REPO.fullmatch(repository) or (repository.lower().startswith("nbtfoundry/")
                                          and repository not in OWN_ALLOWED):
        yield "repository must be owner/name, outside NBTFoundry"
    for key in ("commit", "sdk"):
        if not COMMIT.fullmatch(text(key)):
            yield f"{key} must be a full commit (40 lowercase hex digits)"
    match = VERSION.fullmatch(text("version"))
    if not match or match.group(0) == "0.0.0":
        yield "version must be X.Y.Z, each part below 1000"
    build = text("build")
    if not 0 < len(build) <= 200 or any(ord(c) < 32 for c in build):
        yield "build must be one command line, at most 200 characters"
    for key in ("payload", "package-args"):
        value = entry.get(key, OPTIONAL.get(key))
        if not isinstance(value, str) or not PATH.fullmatch(value) or ".." in value.split("/"):
            yield f"{key} must be a path inside the repository"
    if not isinstance(entry.get("lfs", False), bool):
        yield "lfs must be true or false"
    for key, limit in TEXT_LIMITS.items():
        value = text(key)
        if not 0 < len(value) <= limit or value != value.strip():
            yield f"{key} must be 1 to {limit} characters"
    if entry.get("category") not in CATEGORIES:
        yield f"category must be one of {sorted(CATEGORIES)}"


def matrix_item(app, entry):
    return {"app": app, "repository": entry["repository"], "commit": entry["commit"],
            "version": entry["version"], "sdk": entry["sdk"], "build": entry["build"],
            "payload": entry["payload"], "package-args": entry.get("package-args", OPTIONAL["package-args"]),
            "lfs": entry.get("lfs", False)}


def changed_since(base):
    out = subprocess.run(["git", "-C", str(ROOT), "diff", "--name-only", "--no-renames", base, "--", "apps"],
                         check=True, capture_output=True, text=True).stdout.split()
    return {Path(name).stem for name in out if name.endswith(".json")}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reserved", type=Path)
    parser.add_argument("--base")
    parser.add_argument("--only")
    args = parser.parse_args()
    reserved = {}
    if args.reserved:
        for item in json.loads(args.reserved.read_text(encoding="utf-8")).get("apps", []):
            if item.get("repo") != HERE:
                reserved[item.get("id")] = item.get("repo")
    errors, items = [], []
    for path in sorted((ROOT / "apps").glob("*")):
        if path.name == ".gitkeep":
            continue
        app = path.stem
        try:
            entry = json.loads(path.read_text(encoding="utf-8")) if path.suffix == ".json" else None
        except ValueError as error:
            entry, found = None, [f"not JSON ({error})"]
        else:
            found = list(problems(app, entry, reserved)) if path.suffix == ".json" else ["only .json files"]
        errors += [f"apps/{path.name}: {reason}" for reason in found]
        if not found:
            items.append(matrix_item(app, entry))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    if args.only:
        items = [item for item in items if item["app"] == args.only]
        if not items:
            print(f"no entry {args.only}", file=sys.stderr)
            return 1
    elif args.base:
        changed = changed_since(args.base)
        items = [item for item in items if item["app"] in changed]
    print(json.dumps(items))
    return 0


if __name__ == "__main__":
    sys.exit(main())
