#!/usr/bin/env python3

# MIT License
# Copyright (c) 2020 Jack Rayner <me@jrayner.net>

import time
from subprocess import PIPE, Popen

import iterm2

DEFAULT_REFRESH_INTERVAL = 5.0
TICK_SECONDS = 1.0

applescript = '''set fs to ASCII character 30
if application "Spotify" is running and application "Podcasts" is not running then
	tell application "Spotify"
		if player state is stopped then
			set display to "stopped" & fs & fs & fs
		else
			set track_artist to artist of current track
			set track_name to name of current track
			set track_duration to duration of current track
			set seconds_played to player position
			set state to "playing"
			if player state is paused then
				set state to "paused"
			end if

			set display to state & fs & track_name & fs & track_artist & fs & ¬
				(round ((seconds_played * 1000 / track_duration) * 100))
		end if
	end tell
else
	set display to "closed" & fs & fs & fs
end if'''

def check_spotify():
    p = Popen(['osascript', '-'], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate(applescript.encode('utf-8'))
    if p.returncode != 0:
        return ["error", "", "", "0"]

    # Only strip the trailing newline: `\x1e` is classified as whitespace by
    # str.isspace(), so a bare .strip() would also eat empty leading/trailing
    # fields (e.g. the "closed"/"stopped" cases).
    output = stdout.decode('utf-8').rstrip("\n").split("\x1e")
    if output[0] == "playing":
        output[0] = "♬"
    elif output[0] == "paused":
        output[0] = "☉"
    return output

async def main(connection):
    # Define the configuration knobs:
    vl = "spotify_current_track"
    refresh_key = "spotify_refresh_interval"
    knobs = [
        iterm2.CheckboxKnob("Enable Spotify Track Info", False, vl),
        iterm2.PositiveFloatingPointKnob(
            "Refresh Interval (seconds)", DEFAULT_REFRESH_INTERVAL, refresh_key),
    ]
    component = iterm2.StatusBarComponent(
        short_description="Spotify Current Track",
        detailed_description="Displays the currently playing track information from Spotify",
        knobs=knobs,
        exemplar="♬ Black Betty - Spiderbait (4%)",
        # A fixed, short tick: it's the redraw granularity, not the actual
        # refresh rate -- check_spotify() only re-runs once per the
        # knob-configurable refresh interval, below.
        update_cadence=TICK_SECONDS,
        identifier="com.iterm2.jackrayner.spotify-current-track")

    # This function gets called whenever any of the paths named in defaults (below) changes
    # or its configuration changes.
    # References specify paths to external variables (like rows) and binds them to
    # arguments to the registered function (coro). When any of those variables' values
    # change the function gets called.
    status_messages = {
        "closed": "Spotify Closed",
        "stopped": "No Track Playing",
        "error": "Error",
    }
    state = {"track": None, "last_check": 0.0}

    @iterm2.StatusBarRPC
    async def coro(knobs):
        if vl not in knobs or not knobs[vl]:
            return "✖️ Not Enabled"

        refresh_interval = knobs.get(refresh_key, DEFAULT_REFRESH_INTERVAL)
        now = time.monotonic()
        if state["track"] is None or now - state["last_check"] >= refresh_interval:
            state["track"] = check_spotify()
            state["last_check"] = now
        track = state["track"]

        if track[0] in status_messages:
            return [ f"✖️ {status_messages[track[0]]}", "✖️" ]

        return [ "{} {} - {} ({}%)".format(*track),
                "{0} {1} ({3}%)".format(*track),
                "{} {}".format(*track),
                "{}".format(*track)
        ]

    @iterm2.RPC
    async def on_click(session_id):
        Popen(['osascript', '-e', 'tell application "Spotify" to activate'])

    # Register the component.
    await component.async_register(connection, coro, onclick=on_click)

iterm2.run_forever(main)
