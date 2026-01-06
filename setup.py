"""Setup script for YouTube SEO Tool."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="youtube-seo-tool",
    version="1.0.0",
    author="Deniz & Xenia",
    description="YouTube keyword research tool with Gap Score analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/katarask/youtube-seo-tool",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "yt-seo=src.cli:cli",
        ],
    },
)
