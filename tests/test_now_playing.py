"""Tests for now-playing.py.

Only `check_spotify()` is covered here: it is the one piece of synchronous,
`iterm2`-free logic in the script, and it's exercised by mocking
`subprocess.Popen` so no real `osascript`/Spotify call ever happens.

Deliberately NOT covered: `main()`, the `coro` status-bar callback, and the
`iterm2.StatusBarComponent`/`iterm2.run_forever` registration wiring. Those
only make sense inside iTerm2's bundled Python Runtime talking to a real
iTerm2 process, which isn't something a unit test in CI can meaningfully
exercise -- see AGENTS.md.
"""

import importlib.util
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "now-playing.py"


def _load_now_playing():
    """Load now-playing.py by path, stubbing out the real `iterm2` package.

    The real `iterm2` module only exists inside iTerm2's bundled Python
    Runtime, and the script imports it unconditionally at module level, so a
    fake module must be registered in `sys.modules` before the file is
    loaded.
    """
    fake_iterm2 = types.ModuleType("iterm2")
    fake_iterm2.CheckboxKnob = MagicMock()
    fake_iterm2.StatusBarComponent = MagicMock()
    fake_iterm2.StatusBarRPC = lambda func: func
    fake_iterm2.run_forever = MagicMock()
    sys.modules["iterm2"] = fake_iterm2

    spec = importlib.util.spec_from_file_location("now_playing", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


now_playing = _load_now_playing()


def _mock_popen(stdout: bytes, returncode: int = 0):
    process = MagicMock()
    process.communicate.return_value = (stdout, b"")
    process.returncode = returncode
    return process


def test_check_spotify_playing():
    stdout = b"playing\x1eBlack Betty\x1eSpiderbait\x1e4\n"
    with patch.object(now_playing, "Popen", return_value=_mock_popen(stdout)):
        result = now_playing.check_spotify()

    assert result == ["♬", "Black Betty", "Spiderbait", "4"]


def test_check_spotify_paused():
    stdout = b"paused\x1eBlack Betty\x1eSpiderbait\x1e4\n"
    with patch.object(now_playing, "Popen", return_value=_mock_popen(stdout)):
        result = now_playing.check_spotify()

    assert result == ["☉", "Black Betty", "Spiderbait", "4"]


def test_check_spotify_closed():
    stdout = b"closed\x1e\x1e\x1e\n"
    with patch.object(now_playing, "Popen", return_value=_mock_popen(stdout)):
        result = now_playing.check_spotify()

    assert result == ["closed", "", "", ""]


def test_check_spotify_stopped():
    """Spotify is running but has no track loaded (e.g. never played anything)."""
    stdout = b"stopped\x1e\x1e\x1e\n"
    with patch.object(now_playing, "Popen", return_value=_mock_popen(stdout)):
        result = now_playing.check_spotify()

    assert result == ["stopped", "", "", ""]


def test_check_spotify_error_on_nonzero_returncode():
    with patch.object(
        now_playing, "Popen", return_value=_mock_popen(b"", returncode=1)
    ):
        result = now_playing.check_spotify()

    assert result == ["error", "", "", "0"]


def test_check_spotify_track_name_containing_semicolon():
    """A literal ';' in a track/artist name must not corrupt field parsing.

    The old ';'-delimited format broke on this; the record-separator
    delimiter (0x1e) can't appear in Spotify metadata.
    """
    stdout = b"playing\x1eRock; Roll\x1eArtist\x1e50\n"
    with patch.object(now_playing, "Popen", return_value=_mock_popen(stdout)):
        result = now_playing.check_spotify()

    assert result == ["♬", "Rock; Roll", "Artist", "50"]
