from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# Read version from package
def get_version():
    version_file = os.path.join(os.path.dirname(__file__), "src", "sc2_bootstrap_discord", "__init__.py")
    with open(version_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"')
    return "0.1.0"

setup(
    name="sc2-bootstrap-discord",
    version=get_version(),
    author="Craig Hamilton",
    author_email="craigh@quailholdings.com",
    description="A Discord bot for managing StarCraft 2 matches with local-bootstrap",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/craigham/sc2-discord-bot",
    project_urls={
        "Bug Reports": "https://github.com/craigham/sc2-discord-bot/issues",
        "Source": "https://github.com/craigham/sc2-discord-bot",
    },
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
        "Topic :: Games/Entertainment",
        "Topic :: Communications :: Chat",
    ],
    keywords="starcraft, discord, bot, gaming, ai",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "discord.py>=2.0.0",
        "graypy>=2.1.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    entry_points={
        "console_scripts": [
            "sc2-bootstrap-discord=sc2_bootstrap_discord.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 