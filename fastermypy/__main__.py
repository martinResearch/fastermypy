import os
import subprocess
import toml
from pathlib import Path
import sys
from mypy import api
import time


def load_config():
    """Load fastermypy settings from pyproject.toml."""
    current_dir = Path.cwd()
    while current_dir != current_dir.parent:
        config_file = current_dir / "pyproject.toml"
        if config_file.exists():
            return config_file
        current_dir = current_dir.parent
        if (current_dir / ".git").exists():
            break
    return {}


def find_mypy_config():
    """Search for a mypy.ini file up to the Git root directory."""
    try:
        git_root = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            text=True,
            capture_output=True,
            check=True,
        ).stdout.strip()
        git_root_path = Path(git_root)
    except subprocess.CalledProcessError:
        git_root_path = Path.cwd().root

    current_dir = Path.cwd()
    while current_dir != git_root_path and current_dir != current_dir.parent:
        config_path = current_dir / "mypy.ini"
        if config_path.exists():
            return config_path
        current_dir = current_dir.parent

    config_path = git_root_path / "mypy.ini"
    return config_path if config_path.exists() else None


def get_git_branch():
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


def get_repo_root():
    """Get the root directory of the Git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            text=True,
            capture_output=True,
            check=True,
        )
        return Path(result.stdout.strip()).absolute()
    except subprocess.CalledProcessError:
        return Path.cwd().root


def run_mypy():
    """Run mypy with branch-specific caching and optional pre-command."""
    config_file = load_config()
    print(f"Using fastmypy configurations from {config_file}")
    config_data = toml.load(config_file)
    config = config_data.get("tool", {}).get("fastermypy", {})
    branch_name = get_git_branch()
    repo_root = get_repo_root()
    cache_dir = config.get("cache_dir", "{repo_root}/.mypy_cache/branch/{branch_name}")
    assert isinstance(cache_dir, str)
    cache_dir = cache_dir.format(branch_name=branch_name, repo_root=repo_root)
    os.makedirs(cache_dir, exist_ok=True)
    print(f"Using cache directory: {cache_dir}")

    pre_command = config.get("pre_command")
    if pre_command:
        start = time.time()
        print(f"Running pre-command: {pre_command}")
        # runn command and stop if failed
        out = subprocess.check_call(pre_command, shell=True)
        if out != 0:
            raise Exception("Pre-command failed")
        pre_command_duration = time.time() - start
    config_file = find_mypy_config()

    # Path(cache_dir).mkdir(exist_ok=True)

    # Forward all provided command-line arguments to mypy
    mypy_args = sys.argv[1:]  # Get all command-line arguments after `fastermypy`

    # Build Mypy arguments list
    args = [f"--cache-dir={cache_dir}"]
    if config_file:
        print(f"Using mypy configuration file: {config_file}")
        args.append(f"--config-file={config_file}")
    args.extend(mypy_args)

    print("Running Mypy")
    start = time.time()

    # Run mypy via its API
    stdout, stderr, exit_status = api.run(args)

    end = time.time()

    if stdout:
        print(stdout)
    if stderr:
        print(stderr, file=sys.stderr)

    if pre_command:
        print(f"Pre-command took {pre_command_duration:3g} seconds")
    print(f"Mypy took {end-start:3g} seconds")
    sys.exit(exit_status)


if __name__ == "__main__":
    run_mypy()
