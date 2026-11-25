#!/usr/bin/env python3
# SPDX-License-Identifier: MPL-2.0
"""Reads tag names on stdin; prints the JSON list (argv[1]) without the
applications whose <app>-v<version> tag exists: a release is never redone."""
import json
import sys

tags = set(sys.stdin.read().split())
print(json.dumps([item for item in json.loads(sys.argv[1]) if f"{item['app']}-v{item['version']}" not in tags]))
