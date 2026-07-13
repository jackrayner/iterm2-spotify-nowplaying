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

- Customisable refresh interval.
- Improved error handling(?).
- Investigate replacement of calling `osascript` to get track information.
- Scrolling text.
- Click to open Spotify.
- Add track to saved songs.
