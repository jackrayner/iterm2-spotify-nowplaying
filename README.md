# Spotify Track Info for iTerm2 Status Bar

[![Lint](https://github.com/jackrayner/iterm2-spotify-nowplaying/actions/workflows/lint.yml/badge.svg)](https://github.com/jackrayner/iterm2-spotify-nowplaying/actions/workflows/lint.yml)
[![Test](https://github.com/jackrayner/iterm2-spotify-nowplaying/actions/workflows/test.yml/badge.svg)](https://github.com/jackrayner/iterm2-spotify-nowplaying/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

_Enables Spotify track information in the iTerm2 status bar._

![Main Window](/img/main_window.png "Main Window")

## Features

- Information refresh every 5 seconds by default -- configurable in the
  status bar component's settings.
- Track name, artist and progress (%) information, gracefully dropping
  detail (artist, then progress, then name) as the status bar narrows.
- Click the status bar item to bring Spotify to the front.
- Playing/Paused indicator.
  - ![Status Bar](/img/playing_full.png "Status Bar")
  - ![Status Bar](/img/paused_full.png "Status Bar")
- Application/Integration Status
  - ![Status Bar](/img/spotify_closed.png "Status Bar")
  - ![Status Bar](/img/not_enabled.png "Status Bar")
- Multiple sizes
  - ![Status Bar](/img/playing_full.png "Status Bar")
  - ![Status Bar](/img/reduced_1.png "Status Bar")
  - ![Status Bar](/img/reduced_2.png "Status Bar")
  - ![Status Bar](/img/reduced_3.png "Status Bar")

## Requirements

- iTerm2
- iTerm2 Python Runtime (will be installed on first launch after installation)

## Installation

```sh
curl -fsSL https://raw.githubusercontent.com/jackrayner/iterm2-spotify-nowplaying/main/install.sh | bash
```

If iTerm2's Python API is disabled, the script will offer to enable it for
you (it's required for `now-playing.py` to run at all). Then restart iTerm2
to load the script.

If you'd rather review the script first, or you're working from a clone
(e.g. for development), run it locally instead -- it'll symlink
`now-playing.py` so `git pull` keeps it up to date:

```sh
git clone https://github.com/jackrayner/iterm2-spotify-nowplaying.git
cd iterm2-spotify-nowplaying
./install.sh
```

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, running tests,
linting, and a list of planned future improvements.

## License

[MIT](LICENSE)
