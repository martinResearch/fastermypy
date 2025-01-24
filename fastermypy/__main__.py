"""FasterMypy: Speed up mypy by caching type-checking results per Git branch."""

import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Optional

from mypy import api
import toml


def find_config(repo_root) -> Optional[Path]:
    """Load fastermypy settings from pyproject.toml."""
    current_dir = Path.cwd()
    while current_dir != current_dir.parent:
        config_file = current_dir / "pyproject.toml"
        if config_file.exists():
            return config_file
        current_dir = current_dir.parent
        if current_dir == repo_root:
            break
    return None


def find_mypy_config(repo_root) -> Optional[Path]:
    """Search for a mypy.ini file up to the Git root directory."""
    current_dir = Path.cwd()
    while current_dir != repo_root and current_dir != current_dir.parent:
        config_path = current_dir / "mypy.ini"
        if config_path.exists():
            return config_path
        if current_dir == repo_root:
            break
        current_dir = current_dir.parent

    config_path = repo_root / "mypy.ini"
    return config_path if config_path.exists() else None


def get_git_branch() -> str:
    """Get the current Git branch name."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            text=True,
            capture_output=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "default_branch"


def get_repo_root() -> Path:
    """Get the root directory of the Git repository."""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        text=True,
        capture_output=True,
        check=True,
    )
    return Path(result.stdout.strip()).absolute()


def run_mypy() -> None:
    """Run mypy with branch-specific caching and optional pre-command."""
    branch_name = get_git_branch()
    repo_root = get_repo_root()
    config_file = find_config(repo_root)
    if config_file:
        print(f"Using fastmypy configurations from {config_file}")
        config_data = toml.load(config_file)
        config = config_data.get("tool", {}).get("fastermypy", {})
    else:
        config = None
    cache_dir = config.get("cache_dir", "{repo_root}/.mypy_cache/branch/{branch_name}")
    assert isinstance(cache_dir, str)
    variables = {**os.environ, "branch_name": branch_name, "repo_root": repo_root}
    cache_dir = cache_dir.format(**variables)
    os.makedirs(cache_dir, exist_ok=True)
    print(f"Using cache directory: {cache_dir}")

    if config:
        pre_command = config.get("pre_command")
        if pre_command:
            start = time.time()
            print(f"Running pre-command: {pre_command}")
            # runn command and stop if failed
            out = subprocess.check_call(pre_command, shell=True)
            if out != 0:
                raise Exception("Pre-command failed")
            pre_command_duration = time.time() - start
            print(f"Pre-command took {pre_command_duration:3g} seconds")

    mypy_config_file = find_mypy_config(repo_root)

    # Path(cache_dir).mkdir(exist_ok=True)

    # Forward all provided command-line arguments to mypy
    mypy_args = sys.argv[1:]  # Get all command-line arguments after `fastermypy`

    # Build Mypy arguments list
    args = [f"--cache-dir={cache_dir}"]
    if config_file:
        print(f"Using mypy configuration file: {mypy_config_file}")
        args.append(f"--config-file={mypy_config_file}")

    args.append("--sqlite-cache")  # defaulting this to true as it makes Mypy faster
    args.extend(mypy_args)

    print("Running Mypy with arguments:\n", " ".join(args))
    start = time.time()

    # Run mypy via its API
    stdout, stderr, exit_status = api.run(args)

    end = time.time()
    stdout = stdout.strip()
    if stdout:
        print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)

    print(f"Mypy took {end-start:3g} seconds")
    sys.exit(exit_status)


if __name__ == "__main__":
    run_mypy()
