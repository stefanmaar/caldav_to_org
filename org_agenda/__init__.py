# -*- coding: utf-8 -*-
r"""
Generate Org-Mode agenda file from ical web sources
===================================================

Goal of the script
"""
# Created: Fri Jan 11 22:54:35 2019
# Author: Óscar Nájera
# License:GPL-3

import argparse
import configparser
import hashlib
import logging
import os
import subprocess

import requests
from org_agenda.ical2org import org_events
from org_agenda.cards2org import org_contacts

LOGGER = logging.getLogger("Org_calendar")
LOGGER.addHandler(logging.StreamHandler())


def passwordstore(address: str) -> bytes:
    """Get password from passwordstore address"""

    process = subprocess.run(
        ["pass", "show", address], stdout=subprocess.PIPE, check=True
    )
    if process.returncode == 0:
        return process.stdout.split()[0]

    raise ValueError("Unknown password address")


def download(url, section, force):
    "Return calendar from download or cache"
    hash_url = hashlib.sha1(url.encode("UTF-8")).hexdigest()[:10]
    url_file = f"/tmp/agenda-{hash_url}"
    if not force and os.path.exists(url_file):
        with open(url_file) as txt:
            return txt.read()

    user = section["user"]
    password = passwordstore(section["passwordstore"])

    LOGGER.info("Downloading from: %s", url)

    reply = requests.get(url, auth=(user, password))

    if reply.status_code == 200:
        with open(url_file, "w") as txt:
            txt.write(reply.text)
        return reply.text

    raise ValueError("Could not get calendar: %s" % url)


def get_resource(config, resource, force):
    "RESOURCE{calendars,addressbooks} are returned given the CONFIG's urls, FORCE download"

    for section in config.sections():
        for entry in config[section].get(resource, "").split():
            url = config[section]["url"].format(entry)
            yield download(url, config[section], force)


def write_agenda(config, args):
    "Write the agenda to file"

    calendars = get_resource(config, "calendars", args.force)

    ahead = int(config["DEFAULT"].get("ahead", 50))
    back = int(config["DEFAULT"].get("back", 14))
    outfile = os.path.expanduser(config["DEFAULT"]["agenda_outfile"])

    with open(outfile, "w") as fid:
        LOGGER.info("Writing calendars to: %s", outfile)
        fid.write("\n\n".join(dict.fromkeys(org_events(calendars, ahead, back))))
        fid.write("\n")


def write_addressbook(config, args):
    "Write Contacts to file"
    addresses = get_resource(config, "addressbooks", args.force)
    outfile = os.path.expanduser(config["DEFAULT"]["contacts_outfile"])

    with open(outfile, "w") as fid:
        LOGGER.info("Writing contacts to: %s", outfile)
        fid.write("\n\n".join(org_contacts(addresses)))
        fid.write("\n")


def get_config(filepath):
    "parse config file"

    config = configparser.ConfigParser()

    config_file = os.path.expanduser(filepath)
    LOGGER.info("Reading config from: %s", config_file)
    config.read([config_file])

    return config


def parse_arguments():
    "Parse CLI"
    parser = argparse.ArgumentParser(description="Translate CalDav Agenda to orgfile")
    parser.add_argument(
        "-f", "--force", help="Force Download of Caldav files", action="store_true"
    )
    parser.add_argument(
        "--contacts", action="store_true", help="Download carddav to org-contacts"
    )
    parser.add_argument("-v", "--verbose", action="count", default=0)

    return parser.parse_args()


def main():
    "Transform Calendars"
    args = parse_arguments()

    log_level = logging.INFO if args.verbose > 0 else logging.WARNING
    LOGGER.setLevel(log_level)

    config = get_config("~/.calendars.conf")

    if args.contacts:
        write_addressbook(config, args)

    write_agenda(config, args)
