# AGENTS.md

## What this is

A single iTerm2 status-bar script (`now-playing.py`) that shows the
currently-playing Spotify track. It runs inside iTerm2's own Python Runtime
(not a normal interpreter) and shells out to `osascript` to ask Spotify, via
AppleScript, what's currently playing. There is no CLI, no packaging, and no
inline PEP 723 metadata -- it's installed by symlinking the file into
iTerm2's AutoLaunch folder (see README.md).

## Commands

### Setup

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

There is no `requirements.txt` for `now-playing.py` itself: its only
non-stdlib import, `iterm2`, is bundled with iTerm2's Python Runtime and is
**not on PyPI**. Do not try to `pip install iterm2` locally or in CI -- it
will fail (or silently install an unrelated package).

### Test

```sh
python3 -m pytest
```

### Lint

```sh
ruff check .
```

## Structure

- `now-playing.py` -- the entire status-bar component: `applescript` (the
  template string sent to `osascript`), `check_spotify()` (runs it and
  parses the result), and `main()`/`coro` (the `iterm2` status-bar
  registration and formatting logic).
- `install.sh` -- installs `now-playing.py` into iTerm2's AutoLaunch
  folder (symlinking it when run from a clone, downloading it otherwise)
  and offers to enable iTerm2's Python API if it's off.
- `tests/test_now_playing.py` -- unit tests for `check_spotify()` only.
- `tests/test_install_sh.py` -- runs `install.sh` under `bash` against a
  fake `$HOME`, with `curl`/`defaults` stubbed out on `PATH`.
- `img/` -- screenshots used in README.md.

## Conventions

- `iterm2` can only be imported/run inside iTerm2's bundled Python Runtime.
  It is not installable via pip, so CI never attempts it -- the test suite
  stubs it out in `sys.modules` before loading the script (see
  `tests/test_now_playing.py`). Never add `iterm2` to a requirements file.
- The AppleScript in `applescript` is fragile, string-templated shell
  content that emits four fields delimited by `\x1e` (ASCII record
  separator, chosen because it can't appear in Spotify track/artist
  metadata -- a literal `;` in a track name used to corrupt parsing when
  `;` was the delimiter). The first field is one of `playing`, `paused`,
  `stopped` (Spotify running with no track loaded), `closed` (Spotify not
  running, or Podcasts is running), or `error` (non-zero `osascript` exit,
  synthesized by `check_spotify()` itself rather than the AppleScript). If
  you change the output shape, you must update `check_spotify()`'s parsing
  (the `.split("\x1e")` and index-based lookups), the `coro`
  `status_messages` dict, and the `coro` formatting strings
  (`"{0} {1} - {2} ({3}%)"` etc.) in the same change, or the status bar will
  silently show garbage or raise an `IndexError`.
- `check_spotify()` is the only synchronous, `iterm2`-independent logic, and
  therefore the only thing unit-tested. `main()`/`coro`/the
  `iterm2.StatusBarComponent` registration require a real iTerm2 process and
  can't be meaningfully unit tested -- they're only verified by manual
  end-to-end testing (see CONTRIBUTING.md).
- Manual/E2E testing requires symlinking the script into
  `~/Library/Application Support/iTerm2/Scripts/AutoLaunch/` (per README.md)
  and restarting iTerm2, ideally with Spotify open in each of the
  playing/paused/closed states.
- No type hints are currently used in `now-playing.py`. Match the existing
  (untyped) style if you edit it; if you do add type hints, do so
  consistently across the whole file rather than partially.
