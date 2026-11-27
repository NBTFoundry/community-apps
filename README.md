<!-- SPDX-License-Identifier: MPL-2.0 -->
# NBTFoundry community apps

> **Warning: installing or modifying this software can brick your head unit. Recovery may require professional service or replacement, at your expense. Provided AS IS; use at your own risk, subject to applicable law.**

Applications by other developers, built here from their own repositories and
signed with NBTFoundry's apps key. They install like NBTFoundry's own on any
car with NBT Manager, with no key to add, and the phone app lists them in
Get apps.

## Submit an application

1. **Your repository:** public, built on the [NBT App SDK](https://github.com/NBTFoundry/sdk)
   (start from the [template](https://github.com/NBTFoundry/template)), with
   its `release/package.args`. Its licence must let us publish the built package.
   A `release/notes/X.Y.Z.md` beside it (what the version changes, for a car
   owner) tops the release's page.
2. **A pull request** adding `apps/<id>.json`, where `<id>` is the package's
   `--app`:
   ```json
   {
     "repository": "you/nf-clock",
     "commit": "<the 40-digit commit to build>",
     "version": "1.0.0",
     "sdk": "<the NBTFoundry/sdk commit it builds against>",
     "build": "make -j\"$(nproc)\" module",
     "payload": "build/nbt-clock.so",
     "name": "Clock",
     "summary": "A clock on the iDrive screen.",
     "license": "MPL-2.0",
     "category": "tool"
   }
   ```
   Optional: `"package-args"` (default `release/package.args`), `"lfs": true`
   when the build needs Git LFS files. `category`: `game`, `emulator`, `tool`
   or `system`.
3. **The check** validates the entry and builds your application at that
   commit, without signing it. Its summary shows your package description.
4. **Review and release:** a maintainer reads the source at that commit and
   merges. The release workflow builds it again; once a maintainer approves the
   signing, `<id>-vX.Y.Z` is published here and Get apps lists it.

A new version is a pull request that changes `commit` and raises `version`.

## What the review looks at

- The source at the pinned commit is public and builds the package.
- The id is new: an id NBTFoundry already ships is refused by the check.
- Every capability in `package.args` has a reason, above all MOST messages,
  network ports and car data.
- The application does what its summary says, and nothing else.

To try an application on your own car first, sign it with your own key: the
template's [Your own key](https://github.com/NBTFoundry/template#your-own-key).

## Licence

This repository: [MPL-2.0](LICENSE). Each application keeps its own licence.

Not affiliated with or endorsed by BMW AG. BMW, iDrive and NBT are trademarks
of BMW AG.
