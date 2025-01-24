import os
import subprocess
import toml
from pathlib import Path

def load_config():
    """Load fastermypy settings from pyproject.toml."""
    current_dir = Path.cwd()
    while current_dir != current_dir.parent:
        config_file = current_dir / "pyproject.toml"
        if config_file.exists():
            config_data = toml.load(config_file)
            return config_data.get("tool", {}).get("fastermypy", {})
        current_dir = current_dir.parent
    return {}

def find_mypy_config():
    """Search for a mypy.ini file up to the Git root directory."""
    try:
        git_root = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            text=True, capture_output=True, check=True
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
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            text=True, capture_output=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return "default_branch"

def run_mypy():
    """Run mypy with branch-specific caching and optional pre-command."""
    config = load_config()
    
    branch_name = get_git_branch()
    cache_dir = config.get("cache_dir", f".mypy_cache_{branch_name}")
    os.makedirs(cache_dir, exist_ok=True)

    pre_command = config.get("pre_command")
    if pre_command:
        print(f"Running pre-command: {pre_command}")
        subprocess.run(pre_command, shell=True, check=True)

    config_file = find_mypy_config()
    config_option = f"--config-file={config_file}" if config_file else ""

    command = ["mypy", f"--cache-dir={cache_dir}"]
    if config_option:
        command.append(config_option)
    command.append(".")

    print(f"Running mypy with cache: {cache_dir}")
    if config_file:
        print(f"Using config: {config_file}")

    subprocess.run(command, check=True)

if __name__ == "__main__":
    run_mypy()
