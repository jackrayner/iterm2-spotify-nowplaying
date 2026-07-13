"""Tests for install.sh.

Runs the real script under `bash` (subprocess) against a fake `$HOME`, so
nothing here touches the developer's actual iTerm2 AutoLaunch folder.

The "piped via `curl | bash`" mode is exercised by feeding the script to
`bash` over stdin (so `$0` is `bash`, just like the real curl pipeline) while
skipping the real network call: a stub `curl` executable is put first on
`PATH`, the same way the other test module stubs out `iterm2` -- see
AGENTS.md on why real external dependencies aren't exercised in CI.
"""

import shutil
import subprocess
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


@pytest.fixture
def fake_home(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    return home


def _autolaunch_target(home: Path) -> Path:
    return home / AUTOLAUNCH_SUFFIX / "now-playing.py"


def test_symlinks_now_playing_when_run_from_a_clone(fake_home):
    clone = fake_home.parent / "clone"
    clone.mkdir()
    shutil.copy(SCRIPT_PATH, clone / "install.sh")
    now_playing = clone / "now-playing.py"
    now_playing.write_text("# real script contents\n")

    subprocess.run(
        ["bash", "install.sh"],
        cwd=clone,
        env={"HOME": str(fake_home), "PATH": "/usr/bin:/bin"},
        check=True,
        capture_output=True,
        text=True,
    )

    target = _autolaunch_target(fake_home)
    assert target.is_symlink()
    assert target.resolve() == now_playing.resolve()


def test_rerunning_from_a_clone_is_idempotent(fake_home):
    clone = fake_home.parent / "clone"
    clone.mkdir()
    shutil.copy(SCRIPT_PATH, clone / "install.sh")
    (clone / "now-playing.py").write_text("# real script contents\n")

    for _ in range(2):
        subprocess.run(
            ["bash", "install.sh"],
            cwd=clone,
            env={"HOME": str(fake_home), "PATH": "/usr/bin:/bin"},
            check=True,
            capture_output=True,
            text=True,
        )

    target = _autolaunch_target(fake_home)
    assert target.is_symlink()


def test_downloads_now_playing_when_piped_without_a_clone(fake_home, tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    curl_log = tmp_path / "curl.log"
    curl_stub = bin_dir / "curl"
    curl_stub.write_text(CURL_STUB)
    curl_stub.chmod(0o755)

    with SCRIPT_PATH.open() as script:
        result = subprocess.run(
            ["bash"],
            stdin=script,
            env={
                "HOME": str(fake_home),
                "PATH": f"{bin_dir}:/usr/bin:/bin",
                "CURL_LOG": str(curl_log),
            },
            check=True,
            capture_output=True,
            text=True,
        )

    target = _autolaunch_target(fake_home)
    assert not target.is_symlink()
    assert target.read_text() == "stub-download-content\n"
    assert "now-playing.py" in curl_log.read_text()
    assert "Installed now-playing.py" in result.stdout


def test_creates_autolaunch_directory_if_missing(fake_home):
    assert not (fake_home / AUTOLAUNCH_SUFFIX).exists()

    clone = fake_home.parent / "clone"
    clone.mkdir()
    shutil.copy(SCRIPT_PATH, clone / "install.sh")
    (clone / "now-playing.py").write_text("# real script contents\n")

    subprocess.run(
        ["bash", "install.sh"],
        cwd=clone,
        env={"HOME": str(fake_home), "PATH": "/usr/bin:/bin"},
        check=True,
        capture_output=True,
        text=True,
    )

    assert (fake_home / AUTOLAUNCH_SUFFIX).is_dir()
