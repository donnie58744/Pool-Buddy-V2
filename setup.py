# setup.py
from setuptools import setup, find_packages

setup(
    name="pool-buddy",
    version="0.0.1a",
    author="Donovan Whysong",
    author_email="donnie58744@gmail.com",
    description="A library for monitoring a variety of Pool releated information. Including water temp, outside temp, humidity etc...",
    packages=find_packages(),
    install_requires=[
        "pyowm",
        "requests",
        "RPi.GPIO",
    ],
    python_requires=">=3.12",
)