from setuptools import setup

package = "org-mode-agenda"
version = "0.1"

with open("README.rst", encoding='utf-8') as f:
    long_description = f.read()

with open("requirements.txt") as fp:
    install_requires=fp.read()

setup(
    name=package,
    version=version,
    author="Óscar Nájera",
    author_email="hi@oscarnajera.com",
    description="Import icalendar agendas to Orgmode",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://gitlab.com/Titan-C/org-mode-agenda",
    packages=["org_agenda"],
    entry_points={"console_scripts": ["org_agenda_sync = org_agenda:main"]},
    install_requires=install_requires,
    license="GNU General Public License v3 or later (GPLv3+)",
    classifiers=[
        "Programming Language :: Python :: 3",
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    ],
    python_requires='>=3.6',
)
