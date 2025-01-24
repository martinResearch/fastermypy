# FasterMypy

FasterMypy is a custom wrapper for mypy that provides:

- **Branch-Specific Caching:** Speeds up type checking by maintaining separate caches for each Git branch.
- **Pre-Execution Command Support:** Ensures dependencies are up-to-date before type checking.

## Installation

Install directly from GitHub:

```bash
pip install git+https://github.com/martinResearch/fastermypy.git
```

Replace `yourusername` with your actual GitHub username.

## Configuration

FasterMypy uses the `pyproject.toml` file for configuration. Add the following section to configure it:

```toml
[tool.fastermypy]
cache_dir = ".mypy_cache_{branch}"  # Customize cache directory per branch
pre_command = "uv pip sync requirements.txt"  # Command to run before mypy
```

- `{branch}` in `cache_dir` will be replaced by the current Git branch name.
- `pre_command` allows you to specify any shell command (e.g., dependency synchronization).

## Usage

Once installed, you can run FasterMypy using:

```bash
fastermypy
```

### Example Workflow

1. Add configuration in `pyproject.toml`:

   ```toml
   [tool.fastermypy]
   cache_dir = ".mypy_cache_{branch}"
   pre_command = "uv pip sync requirements.txt"
   ```

2. Run FasterMypy:

   ```bash
   fastermypy
   ```

3. The tool will:
   - Search for `mypy.ini` in the project or parent directories.
   - Set a branch-specific cache directory.
   - Run the pre-configured command before type checking.
   - Execute `mypy` with the appropriate settings.

## Notes

- Ensure your Python environment is activated before running FasterMypy.
- The tool will gracefully handle cases where Git is not available or `pyproject.toml` is not found.

## Contribution

Feel free to contribute by submitting issues and pull requests on GitHub.

---

**License:** MIT License
