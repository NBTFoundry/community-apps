#!/usr/bin/env python3
# SPDX-License-Identifier: MPL-2.0
"""Markdown for the pull request's summary: each changed application's source
and package description (capabilities, MOST, network, settings) at its pinned
commit, which the reviewer reads before approving."""
import json
import sys
import urllib.request

for item in json.loads(sys.argv[1]):
    url = f"https://raw.githubusercontent.com/{item['repository']}/{item['commit']}/{item['package-args']}"
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            text = response.read(8192).decode("utf-8", "replace")
    except OSError as error:
        text = f"(not readable: {error})"
    print(f"### {item['app']} {item['version']}\n\n"
          f"https://github.com/{item['repository']}/tree/{item['commit']}\n\n"
          f"Build `{item['build']}`, payload `{item['payload']}`\n\n```\n{text.replace('```', '` ` `')}\n```\n")
