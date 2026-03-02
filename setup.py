# setup.py
from setuptools import setup, find_packages

setup(
    name="pool-buddy",
    version="0.0.1a3",
    author="Donovan Whysong",
    author_email="donnie58744@gmail.com",
    description="A library for monitoring a variety of Pool releated information. Including water temp, outside temp, humidity etc...",
    url="https://github.com/donnie58744/Pool-Buddy-V2",
    project_urls={
        "Bug Tracker": "https://github.com/donnie58744/Pool-Buddy-V2/issues",
        "Documentation": "https://github.com/donnie58744/Pool-Buddy-V2#readme",
        "Source Code": "https://github.com/donnie58744/Pool-Buddy-V2",
    },

    packages=find_packages(),

    package_data={
        "pool_buddy_qt": ["ui/*.ui"],
    },

    install_requires=[
        "pyowm>=3.3.0",
        "requests>=2.32.3",
    ],

    extras_require={
        "rpi-qt" : [
            "PyQt5>=5.15",
            "RPi.GPIO",
        ],
        "rpi" : [
            "RPi.GPIO",
        ],
        "dev-qt" : [
            "PyQt5>=5.15",
        ],
        "dev" : [
            
        ]
    },
    
    entry_points={
        "console_scripts": [
            "pool-buddy-qt=pool_buddy_qt.main:main",  # Only works if PyQt5 installed
        ],
    },

    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Home Automation",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],

    keywords="pool monitoring temperature humidity sensors automation",
    
    python_requires=">=3.12",

    license="Apache 2.0",
)