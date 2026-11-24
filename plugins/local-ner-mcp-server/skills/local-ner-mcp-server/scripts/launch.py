"""Prepare the pinned Python runtime and launch the bundled MCP server."""

import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_RUNTIME_DIR = Path.home() / ".codex" / "local-ner-mcp-server" / "plugin-runtime"


def runtime_python(runtime_dir):
    requirements = SCRIPT_DIR / "requirements.txt"
    runtime_identity = f"{Path(sys.executable).resolve()}\n{sys.version}\n".encode()
    digest = hashlib.sha256(runtime_identity + requirements.read_bytes()).hexdigest()[:16]
    environment = runtime_dir / digest
    python_path = Path("Scripts/python.exe") if os.name == "nt" else Path("bin/python")
    interpreter = environment / python_path
    if interpreter.is_file():
        return interpreter

    runtime_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="setup-", dir=runtime_dir) as temporary:
        staging = Path(temporary) / "venv"
        subprocess.run(
            [sys.executable, "-m", "venv", str(staging)],
            stdin=subprocess.DEVNULL,
            stdout=sys.stderr,
            check=True,
        )
        subprocess.run(
            [
                str(staging / python_path), "-m", "pip", "--disable-pip-version-check",
                "install", "--no-input", "--no-cache-dir", "-r", str(requirements),
            ],
            stdin=subprocess.DEVNULL,
            stdout=sys.stderr,
            check=True,
        )
        try:
            staging.rename(environment)
        except OSError:
            if not interpreter.is_file():
                raise
    return interpreter


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runtime-dir", type=Path, default=DEFAULT_RUNTIME_DIR)
    parser.add_argument("--data-dir", type=Path)
    parser.add_argument("--setup", action="store_true", help="Prepare the runtime, then exit.")
    args = parser.parse_args()

    if sys.version_info < (3, 10):
        parser.exit(1, "Local NER MCP Server 需要 Python 3.10 或更新版本。\n")
    try:
        interpreter = runtime_python(args.runtime_dir.expanduser().resolve())
        if args.setup:
            return
        command = [str(interpreter), "-B", str(SCRIPT_DIR / "server.py")]
        if args.data_dir is not None:
            command.extend(["--data-dir", str(args.data_dir.expanduser().resolve())])
        os.execv(command[0], command)
    except (OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Local NER MCP Server 啟動失敗。{error}\n")


if __name__ == "__main__":
    main()
