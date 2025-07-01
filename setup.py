from setuptools import setup
setup(
    name='henelySchedule',
    version='0.1.0',
    packages=['henleySchedule'],
    entry_points={
        'console_scripts': [
            'henleySchedule = henleySchedule.__main__:main'
        ]
    },
    install_requires=[
        "requests",
        "beautifulsoup4",
        "tabulate",
        "colorama",
        "rich",
        "appdirs",
        "pytz",
        "pyyaml"
    ],
    python_requires=">=3.10.0",
    description="""This script fetches and displays the race timetable for the Henley Royal Regatta.
    It allows users to search for specific crews and displays the race schedule in both GB and local 
    times based on the specified GMT offset. Run this script after the draw is published to get the latest results.""")
