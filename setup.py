from setuptools import setup

package = "caldav_to_org"
version = "0.1"

setup(
    name=package,
    version=version,
    author="Óscar Nájera, Stefan Mertl",
    author_email="hi@oscarnajera.com,stefan@mertl-research.at",
    description="Import icalendar agendas to Orgmode",
    long_description="",
    url="https://github.com/stefanmaar/caldav_to_org.git",
    packages=["caldav_to_org"],
    entry_points={"console_scripts": ["caldav_to_org = caldav_to_org:main"]},
    install_requires=["requests", "icalendar", "tzlocal", "vobject", "aiohttp"],
    license="GNU General Public License v3 or later (GPLv3+)",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    ],
    python_requires=">=3.8",
)
