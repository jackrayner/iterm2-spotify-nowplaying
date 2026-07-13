# Contributing

## Development setup

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Note: `now-playing.py`'s own runtime dependency, `iterm2`, is bundled with
iTerm2's Python Runtime and is not available on PyPI, so it isn't (and can't
be) listed in a requirements file. The dev setup above only installs test
tooling.

## Running tests

```sh
python3 -m pytest
```

Tests cover `check_spotify()` by mocking `subprocess.Popen`. Manual
end-to-end testing of the status-bar component itself (the `iterm2`
registration, live formatting, refresh cadence, etc.) requires an actual
iTerm2 + Spotify installation, since the `iterm2` runtime and Spotify's
AppleScript integration can't be exercised in CI. To test manually, run `./install.sh`
from your clone (it symlinks the script into iTerm2's AutoLaunch folder so
local edits take effect immediately) and restart iTerm2.

## Linting

This project uses [ruff](https://docs.astral.sh/ruff/) for Python linting and
[markdownlint](https://github.com/DavidAnson/markdownlint) for Markdown files.

```sh
ruff check .
```

## Pull requests

- Keep changes focused and add tests for new behaviour.
- Make sure `ruff check .` and `python3 -m pytest` both pass before opening a PR.
- CI runs both automatically on every push and pull request.

## Future improvements

Ideas not yet implemented, kept here for reference:

- Investigate replacement of calling `osascript` to get track information.
  Alternatives (Spotify's distributed notifications, MediaRemote, the Web
  API) all trade the current zero-dependency simplicity for `pyobjc` or
  OAuth/network complexity inside a Python runtime whose packaging you don't
  control (see AGENTS.md). Only worth it if `osascript`'s latency/CPU cost
  becomes an actual problem.
- Add track to saved songs. Spotify's AppleScript dictionary has no "save to
  library" verb, so this needs the Spotify Web API with OAuth and token
  storage -- turning a read-only status widget into an authenticated
  read-write client. A bigger scope change than the rest of this list.

## Already tried and abandoned

- Scrolling/marquee text for long track/artist names. Implemented and
  iterated on across several PRs, but never rendered reliably: the status
  bar RPC only returns candidate strings for iTerm2 to pick from ("the
  longest one that fits"), with no control over pixel-level layout. In a
  proportional-width font, the rendered width of same-length scrolled
  substrings wobbles tick to tick, which caused tier selection to flicker
  (blank renders, snapping to a shorter/different string, right-edge
  blanking) in ways that were hard to fully diagnose without deeper access
  to iTerm2's native rendering internals. Reverted in favour of the
  original static field-dropping degradation (drop artist, then progress,
  then name). If revisited, it'd need either pixel-stable candidate widths
  or a different rendering mechanism entirely, not just further tuning.
