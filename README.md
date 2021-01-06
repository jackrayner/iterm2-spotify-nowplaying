# Spotify Track Info for iTerm2 Status Bar

_Enables Spotify track information in the iTerm2 status bar._

![Main Window](https://s3.jrayner.net/iterm2-spotify-nowplaying/main_window.png "Main Window")

## Prerequisites

- iTerm2
- iTerm2 Python Runtime (Will be installed on first launch after installation)

## Installation

```
git clone https://github.com/jackrayner/iterm2-spotify-nowplaying.git
cd iterm2-spotify-nowplaying
mkdir -p ~/Library/Application\ Support/iTerm2/Scripts/AutoLaunch
ln -s "${PWD}/now-playing.py" ~/Library/Application\ Support/iTerm2/Scripts/AutoLaunch/now-playing.py
```

## Features

- Information refresh every 5 seconds.
- Track name, artist and progress (%) information.
- Playing/Paused indicator.
  - ![Status Bar](https://s3.jrayner.net/iterm2-spotify-nowplaying/playing_full.png "Status Bar")
  - ![Status Bar](https://s3.jrayner.net/iterm2-spotify-nowplaying/paused_full.png "Status Bar")
- Application/Integration Status
  - ![Status Bar](https://s3.jrayner.net/iterm2-spotify-nowplaying/spotify_closed.png "Status Bar")
  - ![Status Bar](https://s3.jrayner.net/iterm2-spotify-nowplaying/not_enabled.png "Status Bar")
- Multiple sizes
  - ![Status Bar](https://s3.jrayner.net/iterm2-spotify-nowplaying/playing_full.png "Status Bar")
  - ![Status Bar](https://s3.jrayner.net/iterm2-spotify-nowplaying/reduced_1.png "Status Bar")
  - ![Status Bar](https://s3.jrayner.net/iterm2-spotify-nowplaying/reduced_2.png "Status Bar")
  - ![Status Bar](https://s3.jrayner.net/iterm2-spotify-nowplaying/reduced_3.png "Status Bar")

## TODO - Future improvements

- Customisable refresh interval.
- Improved error handling(?).
- Investigate replacement of calling `osascript` to get track information.
- Travis CI testing.
- Scrolling text.
- Click to open Spotify.
- Add track to saved songs.
