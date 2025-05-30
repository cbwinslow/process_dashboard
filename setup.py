"""Setup configuration for Process Dashboard."""

import os
from setuptools import setup, find_packages

def read(fname):
    """Read file content."""
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()

def get_version():
    """Get version from VERSION file."""
    with open('VERSION') as f:
        return f.read().strip()

setup(
    name="process-dashboard",
    version=get_version(),
    author="System Administrator",
    author_email="admin@example.com",
    description="A matrix-themed system process management dashboard",
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    license="MIT",
    keywords="process monitor system dashboard matrix tui",
    url="https://github.com/yourusername/process-dashboard",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=[
        "textual>=0.9.0",
        "psutil>=5.8.0",
        "rich>=10.0.0",
    ],
    entry_points={
        "console_scripts": [
            "process-dashboard=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: System :: Monitoring",
    ],
)
