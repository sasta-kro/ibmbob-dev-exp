"""
Setup script for Codebase Analyzer
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="codebase-analyzer",
    version="1.0.0",
    description="AI-powered codebase analysis and documentation generator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="IBM Bob",
    python_requires=">=3.10",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "flet>=0.21.0",
        "pydantic>=2.0.0",
        "python-dotenv>=1.0.0",
        "loguru>=0.7.0",
        "pathspec>=0.11.0",
        "chardet>=5.0.0",
        "gitignore-parser>=0.1.0",
        "tree-sitter>=0.20.0",
        "tree-sitter-python>=0.20.0",
        "tree-sitter-javascript>=0.20.0",
        "tree-sitter-typescript>=0.20.0",
        "pylint>=3.0.0",
        "radon>=6.0.0",
        "bandit>=1.7.0",
        "mypy>=1.8.0",
        "ibm-watson>=8.0.0",
        "ibm-cloud-sdk-core>=3.18.0",
        "requests>=2.31.0",
        "aiohttp>=3.9.0",
        "tenacity>=8.2.0",
        "jinja2>=3.1.0",
        "markdown-it-py>=3.0.0",
        "pygments>=2.17.0",
        "jsonschema>=4.20.0",
        "pyyaml>=6.0.0",
        "plotly>=5.18.0",
        "click>=8.1.0",
        "tqdm>=4.66.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "black>=23.0.0",
            "isort>=5.13.0",
            "flake8>=7.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "codebase-analyzer=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)

# Made with Bob
