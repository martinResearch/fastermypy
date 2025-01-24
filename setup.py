from setuptools import setup, find_packages

setup(
    name="fastermypy",
    version="0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "fastermypy=fastermypy.main:run_mypy",
        ],
    },
    install_requires=[
        "mypy",
        "toml"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
