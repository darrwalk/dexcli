from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dexcli",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="DEX Command Line Interface for cryptocurrency trading",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/darrwalk/dexcli",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Office/Business :: Financial :: Investment",
    ],
    python_requires=">=3.8",
    install_requires=[
        "ccxt>=4.0.0",
        "click>=8.0.0",
        "tabulate>=0.9.0",
        "python-dotenv>=0.19.0",
    ],
    entry_points={
        "console_scripts": [
            "dexcli=dexcli.cli:cli",
        ],
    },
)
