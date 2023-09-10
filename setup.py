from pathlib import Path

from setuptools import find_packages, setup

# Get the directory where setup.py is located
current_directory = Path(__file__).parent

# Load the version from file using absolute path
__version__ = (current_directory / "VERSION").read_text().strip()

# Load packages using absolute path
packages = (current_directory / "requirements.txt").read_text().splitlines()

setup(
    name="riffusion",
    packages=find_packages(exclude=[]),
    version=__version__,
    license="MIT",
    description="Riffusion - Stable diffusion for real-time music generation",
    author="Hayk Martiros",
    author_email="hayk.mart@gmail.com",
    long_description_content_type="text/markdown",
    url="https://github.com/riffusion/riffusion",
    keywords=[
        "artificial intelligence",
        "audio generation",
        "music",
        "diffusion",
        "riffusion",
        "deep learning",
        "transformers",
    ],
    install_requires=packages,
    package_data={
        "riffusion": ["py.typed"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
    ],
)
