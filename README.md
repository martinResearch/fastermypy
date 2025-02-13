# FasterMypy

FasterMypy is a custom wrapper for mypy that provides:

- **Branch-Specific Caching:** Speeds up type checking after switching branches by maintaining separate caches for each Git branch.
- **Pre-Execution Command Support:** Ensures dependencies are up-to-date before type checking.
- **Search for the mypy.ini file in the parent folders**: You don't have to run mypy from the folder that contains the `mypy.ini` file.

The goal is to provide a temporary solution to https://github.com/python/mypy/issues/18526 until this eventually get supported by mypy.


## Installation

Install directly from GitHub:

```bash
pip install git+https://github.com/martinResearch/fastermypy.git
```

Replace `yourusername` with your actual GitHub username.

## Configuration

By default fastermypy with use folder  `{repo_root}/.mypy_cache_{branch_name}` for the mypy caching. 
FasterMypy uses the `pyproject.toml` file for configuration. Add the following section to configure it:

```toml
[tool.fastermypy]
# Customize cache directory per branch
cache_dir = "{repo_root}/.mypy_cache/python_{python_path_md5}/branch/{branch_name}"
# Commands to run before mypy
pre_commands = ["uv pip install -r requirements.txt"]  
```

- One can use variables while defining `cache_dir`. The availabel variables are `branch_name`, `repo_root`, `python_path_md5` and all the environment variables. This allow a better control of the caching folder throught the `pyproject.toml` file.
- `pre_commands` allows you to specify any shell command (e.g., dependency synchronization).

## Usage

Once installed, you can run FasterMypy using:

```bash
fastermypy
```

### Example Workflow

1. Add a configuration in `pyproject.toml`:

```toml
[tool.fastermypy]
# Customize cache directory per branch
cache_dir =  "{repo_root}/.mypy_cache/python_{python_path_md5}/branch/{branch_name}" 
# Commands to run before mypy
pre_commands = ["uv pip install -r requirements.txt"]  
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

## Limitations

- the first run of fastmypy in a new branch will be slow because it cannot reuse the cache from the previous branch
- the cache folder size can grow very large as one create many branches and one may need to manually delete the cache for old branches to free space. 

## Contribution

Feel free to contribute by submitting issues and pull requests on GitHub.

---

**License:** MIT License
