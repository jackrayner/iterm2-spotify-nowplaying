# Spotify Track Info for iTerm2 Status Bar

[![Lint](https://github.com/jackrayner/iterm2-spotify-nowplaying/actions/workflows/lint.yml/badge.svg)](https://github.com/jackrayner/iterm2-spotify-nowplaying/actions/workflows/lint.yml)
[![Test](https://github.com/jackrayner/iterm2-spotify-nowplaying/actions/workflows/test.yml/badge.svg)](https://github.com/jackrayner/iterm2-spotify-nowplaying/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

_Enables Spotify track information in the iTerm2 status bar._

![Main Window](/img/main_window.png "Main Window")

## Features

- Information refresh every 5 seconds.
- Track name, artist and progress (%) information.
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
git clone https://github.com/jackrayner/iterm2-spotify-nowplaying.git
cd iterm2-spotify-nowplaying
mkdir -p ~/Library/Application\ Support/iTerm2/Scripts/AutoLaunch
ln -s "${PWD}/now-playing.py" ~/Library/Application\ Support/iTerm2/Scripts/AutoLaunch/now-playing.py
```

## Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, running tests,
linting, and a list of planned future improvements.

## License

[MIT](LICENSE)
