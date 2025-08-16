#!/usr/bin/env python3
"""
Setup script for TranslateCore

Installation:
    pip install .
    pip install -e .  # Development mode
"""

from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

# Read requirements
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="translatecore",
    version="1.0.0",
    author="AI Assistant",
    author_email="ai@translatecore.dev",
    description="A powerful multilingual translation library with offline and online capabilities",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/translatecore",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/translatecore/issues",
        "Documentation": "https://github.com/yourusername/translatecore/tree/main/docs",
        "Source Code": "https://github.com/yourusername/translatecore",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "isort>=5.0",
            "flake8>=4.0",
            "mypy>=0.900",
            "pre-commit>=2.0",
        ],
        "docker": [
            "docker>=5.0",
            "docker-compose>=1.29",
        ],
        "all": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=22.0",
            "isort>=5.0", 
            "flake8>=4.0",
            "mypy>=0.900",
            "pre-commit>=2.0",
            "docker>=5.0",
            "docker-compose>=1.29",
        ]
    },
    entry_points={
        "console_scripts": [
            "translatecore=translatecore.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "translatecore": [
            "*.json",
            "configs/*.json",
        ],
    },
    zip_safe=False,
    keywords="translation translate offline online argos deepl google multilingual",
)
