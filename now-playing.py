#!/usr/bin/env python3

# MIT License
# Copyright (c) 2020 Jack Rayner <me@jrayner.net>

import iterm2
from subprocess import Popen, PIPE

applescript = '''if application "Spotify" is running and application "Podcasts" is not running then
	tell application "Spotify"
		if player state is stopped then
			set display to "No Track Playing"
		else
			set track_artist to artist of current track
			set track_name to name of current track
			set track_duration to duration of current track
			set seconds_played to player position
			set state to "playing"
			if player state is paused then
				set state to "paused"
			end if

			set display to state & ";" & track_name & ";" & track_artist & ";" & (round ((seconds_played * 1000 / track_duration) * 100))
		end if
	end tell
else
	set display to "closed;;;"
end if'''

def check_spotify():
    p = Popen(['osascript', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate(applescript.encode('utf-8'))
    if p.returncode == 0:
        output = stdout.decode('utf-8').strip().split(";")
        if output[0] == "playing":
            output[0] = "♬"
        elif output[0] == "paused":
            output[0] = "☉"
        return output
    else:
        return "error"

async def main(connection):
    # Define the configuration knobs:
    vl = "spotify_current_track"
    knobs = [iterm2.CheckboxKnob("Spotify Current Track", False, vl)]
    component = iterm2.StatusBarComponent(
        short_description="Spotify Current Track",
        detailed_description="Displays the currently playing track from Spotify",
        knobs=knobs,
        exemplar="♬ Black Betty - Spiderbait (4%)",
        update_cadence=5,
        identifier="com.iterm2.jackrayner.spotify-current-track")

    # This function gets called whenever any of the paths named in defaults (below) changes
    # or its configuration changes.
    # References specify paths to external variables (like rows) and binds them to
    # arguments to the registered function (coro). When any of those variables' values
    # change the function gets called.
    @iterm2.StatusBarRPC
    async def coro(knobs):
        if vl in knobs and knobs[vl]:
            l = check_spotify()
            if l[0] == "closed":
                return [ "✖️ Spotify Closed", "✖️" ]
            else:
                return [ "{0} {1} - {2} ({3}%)".format(*l),
                        "{0} {1} ({3}%)".format(*l),
                        "{0} {1}".format(*l),
                        "{0}".format(*l)
                ]
        return "✖️ Not Enabled"

    # Register the component.
    await component.async_register(connection, coro)

iterm2.run_forever(main)