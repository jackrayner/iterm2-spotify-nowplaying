"""Tests for install.sh.

Runs the real script under `bash` (subprocess) against a fake `$HOME`, so
nothing here touches the developer's actual iTerm2 AutoLaunch folder.

The "piped via `curl | bash`" mode is exercised by feeding the script to
`bash` over stdin (so `$0` is `bash`, just like the real curl pipeline).
Real external commands (`curl`, `defaults`) are replaced with stub
executables put first on `PATH`, the same way the other test module stubs
out `iterm2` -- see AGENTS.md on why real external dependencies aren't
exercised in CI. Stubbing `defaults` also means these tests never read or
write the developer's actual `com.googlecode.iterm2` preferences.

The "confirm the Python API prompt" tests attach the script's stdin/stdout
to a pty: install.sh reads the prompt answer from `/dev/tty` specifically
so the prompt still works when the script itself is piped into `bash` over
stdin, and a plain pipe/devnull stdin can't stand in for a controlling
terminal.
"""

import os
import pty
import select
import shutil
import subprocess
import time
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).resolve().parent.parent / "install.sh"
AUTOLAUNCH_SUFFIX = Path("Library/Application Support/iTerm2/Scripts/AutoLaunch")

CURL_STUB = """\
#!/usr/bin/env bash
set -euo pipefail
out=""
url=""
while [ $# -gt 0 ]; do
    case "$1" in
        -o) out="$2"; shift 2 ;;
        -*) shift ;;
        *) url="$1"; shift ;;
    esac
done
echo "$url" >> "$CURL_LOG"
echo "stub-download-content" > "$out"
"""

DEFAULTS_STUB = """\
#!/usr/bin/env bash
set -euo pipefail
echo "$@" >> "$DEFAULTS_LOG"
if [ "$1" = "read" ]; then
    echo "${DEFAULTS_READ_VALUE:-0}"
    exit "${DEFAULTS_READ_EXIT:-1}"
fi
"""


@pytest.fixture
def fake_home(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    return home


@pytest.fixture
def stub_bin(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for name, contents in (("curl", CURL_STUB), ("defaults", DEFAULTS_STUB)):
        stub = bin_dir / name
        stub.write_text(contents)
        stub.chmod(0o755)
    return bin_dir


@pytest.fixture
def clone(fake_home):
    clone_dir = fake_home.parent / "clone"
    clone_dir.mkdir()
    shutil.copy(SCRIPT_PATH, clone_dir / "install.sh")
    (clone_dir / "now-playing.py").write_text("# real script contents\n")
    return clone_dir


def _autolaunch_target(home: Path) -> Path:
    return home / AUTOLAUNCH_SUFFIX / "now-playing.py"


def _base_env(fake_home, stub_bin, tmp_path, *, api_enabled):
    return {
        "HOME": str(fake_home),
        "PATH": f"{stub_bin}:/usr/bin:/bin",
        "CURL_LOG": str(tmp_path / "curl.log"),
        "DEFAULTS_LOG": str(tmp_path / "defaults.log"),
        "DEFAULTS_READ_VALUE": "1" if api_enabled else "0",
        "DEFAULTS_READ_EXIT": "0" if api_enabled else "1",
    }


def test_symlinks_now_playing_when_run_from_a_clone(fake_home, stub_bin, clone, tmp_path):
    subprocess.run(
        ["bash", "install.sh"],
        cwd=clone,
        env=_base_env(fake_home, stub_bin, tmp_path, api_enabled=True),
        check=True,
        capture_output=True,
        text=True,
    )

    target = _autolaunch_target(fake_home)
    assert target.is_symlink()
    assert target.resolve() == (clone / "now-playing.py").resolve()


def test_rerunning_from_a_clone_is_idempotent(fake_home, stub_bin, clone, tmp_path):
    env = _base_env(fake_home, stub_bin, tmp_path, api_enabled=True)
    for _ in range(2):
        subprocess.run(
            ["bash", "install.sh"],
            cwd=clone,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )

    assert _autolaunch_target(fake_home).is_symlink()


def test_downloads_now_playing_when_piped_without_a_clone(fake_home, stub_bin, tmp_path):
    env = _base_env(fake_home, stub_bin, tmp_path, api_enabled=True)

    with SCRIPT_PATH.open() as script:
        result = subprocess.run(
            ["bash"],
            stdin=script,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )

    target = _autolaunch_target(fake_home)
    assert not target.is_symlink()
    assert target.read_text() == "stub-download-content\n"
    assert "now-playing.py" in Path(env["CURL_LOG"]).read_text()
    assert "Installed now-playing.py" in result.stdout


def test_creates_autolaunch_directory_if_missing(fake_home, stub_bin, clone, tmp_path):
    assert not (fake_home / AUTOLAUNCH_SUFFIX).exists()

    subprocess.run(
        ["bash", "install.sh"],
        cwd=clone,
        env=_base_env(fake_home, stub_bin, tmp_path, api_enabled=True),
        check=True,
        capture_output=True,
        text=True,
    )

    assert (fake_home / AUTOLAUNCH_SUFFIX).is_dir()


def test_skips_prompt_when_api_already_enabled(fake_home, stub_bin, clone, tmp_path):
    env = _base_env(fake_home, stub_bin, tmp_path, api_enabled=True)

    result = subprocess.run(
        ["bash", "install.sh"],
        cwd=clone,
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "already enabled" in result.stdout
    log_lines = Path(env["DEFAULTS_LOG"]).read_text().splitlines()
    assert log_lines == ["read com.googlecode.iterm2 EnableAPIServer"]


def test_prints_hint_and_skips_write_when_no_tty_available(fake_home, stub_bin, clone, tmp_path):
    env = _base_env(fake_home, stub_bin, tmp_path, api_enabled=False)

    result = subprocess.run(
        ["bash", "install.sh"],
        cwd=clone,
        env=env,
        stdin=subprocess.DEVNULL,
        check=True,
        capture_output=True,
        text=True,
    )

    assert "no terminal is available to prompt" in result.stdout
    assert "defaults write com.googlecode.iterm2 EnableAPIServer -bool true" in result.stdout
    log_lines = Path(env["DEFAULTS_LOG"]).read_text().splitlines()
    assert log_lines == ["read com.googlecode.iterm2 EnableAPIServer"]


def _run_with_pty_reply(clone, env, reply: str, timeout: float = 5.0) -> str:
    """Run install.sh with its stdio attached to a pty and feed it `reply`.

    install.sh reads the enable-API prompt from /dev/tty rather than
    stdin, so a plain pipe can't answer it -- only a real (pseudo)terminal
    can, which is what this simulates.
    """
    master, slave = pty.openpty()
    try:
        process = subprocess.Popen(
            ["bash", "install.sh"],
            cwd=clone,
            env=env,
            stdin=slave,
            stdout=slave,
            stderr=slave,
            start_new_session=True,
        )
        os.close(slave)
        slave = None
        os.write(master, f"{reply}\n".encode())

        output = b""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline and process.poll() is None:
            ready, _, _ = select.select([master], [], [], 0.2)
            if ready:
                try:
                    chunk = os.read(master, 4096)
                except OSError:
                    break
                if not chunk:
                    break
                output += chunk

        process.wait(timeout=timeout)
        try:
            while True:
                chunk = os.read(master, 4096)
                if not chunk:
                    break
                output += chunk
        except OSError:
            pass
        assert process.returncode == 0
        return output.decode()
    finally:
        if slave is not None:
            os.close(slave)
        os.close(master)


def test_enables_api_server_when_user_confirms_via_tty(fake_home, stub_bin, clone, tmp_path):
    env = _base_env(fake_home, stub_bin, tmp_path, api_enabled=False)

    output = _run_with_pty_reply(clone, env, "y")

    assert "Enabled iTerm2's Python API." in output
    log_lines = Path(env["DEFAULTS_LOG"]).read_text().splitlines()
    assert log_lines == [
        "read com.googlecode.iterm2 EnableAPIServer",
        "write com.googlecode.iterm2 EnableAPIServer -bool true",
    ]


def test_skips_write_when_user_declines_via_tty(fake_home, stub_bin, clone, tmp_path):
    env = _base_env(fake_home, stub_bin, tmp_path, api_enabled=False)

    output = _run_with_pty_reply(clone, env, "n")

    assert "Skipped enabling iTerm2's Python API." in output
    log_lines = Path(env["DEFAULTS_LOG"]).read_text().splitlines()
    assert log_lines == ["read com.googlecode.iterm2 EnableAPIServer"]
