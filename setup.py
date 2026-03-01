# setup.py
from setuptools import setup, find_packages

setup(
    name="pool-buddy",
    version="0.0.1a0",
    author="Donovan Whysong",
    author_email="donnie58744@gmail.com",
    description="A library for monitoring a variety of Pool releated information. Including water temp, outside temp, humidity etc...",
    packages=find_packages(),
    install_requires=[
        "pyowm",
        "requests",
        "RPi.GPIO",
    ],

    extras_require={
        "qt": [
            "PyQt5>=5.15",
        ],
    },
    
    entry_points={
        "console_scripts": [
            "pool-buddy-qt=pool_buddy_qt.main:main",  # Only works if PyQt5 installed
        ],
    },
    
    python_requires=">=3.12",
)