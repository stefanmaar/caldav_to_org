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
import asyncio
import configparser
import hashlib
import logging
import os

import requests
import aiohttp

from org_agenda.ical2org import org_events
from org_agenda.cards2org import org_contacts

LOGGER = logging.getLogger("Org_calendar")
LOGGER.addHandler(logging.StreamHandler())


async def passwordstore(address: str) -> str:
    """Get password from passwordstore address"""

    process = await asyncio.create_subprocess_shell(
        f"pass show {address}", stdout=asyncio.subprocess.PIPE
    )
    stdout, _ = await process.communicate()

    if process.returncode == 0:
        return stdout.decode("utf-8").split()[0]

    raise ValueError("Unknown password address")


async def download(url, section, force, session):
    "Return calendar from download or cache"
    hash_url = hashlib.sha1(url.encode("UTF-8")).hexdigest()[:10]
    url_file = f"/tmp/agenda-{hash_url}"
    if not force and os.path.exists(url_file):
        with open(url_file) as txt:
            return txt.read()

    user = section["user"]
    password = await passwordstore(section["passwordstore"])

    LOGGER.info("Downloading from: %s", url)
    async with session.get(url, auth=aiohttp.BasicAuth(user, password)) as reply:
        if reply.status == 200:
            text = await reply.text()
            with open(url_file, "w") as txt:
                txt.write(text)
            return text

        raise ValueError(f"Could not get calendar: {url}\n{reply}")


async def get_resource(config, resource, force):
    "RESOURCE{calendars,addressbooks} are returned given the CONFIG's urls, FORCE download"

    cal = []
    async with aiohttp.ClientSession() as session:
        for section in config.sections():
            for entry in config[section].get(resource, "").split():
                url = config[section]["url"].format(entry)
                cal.append(download(url, config[section], force, session))

        return await asyncio.gather(*cal)


def write_agenda(config, args):
    "Write the agenda to file"

    if args.url:
        calendars = [requests.get(args.url, auth=("username", "")).text]
    else:
        calendars = asyncio.run(get_resource(config, "calendars", args.force))

    ahead = int(config["DEFAULT"].get("ahead", 50))
    back = int(config["DEFAULT"].get("back", 14))
    outfile = os.path.expanduser(config["DEFAULT"]["agenda_outfile"])

    if args.url:
        print("\n\n".join(dict.fromkeys(org_events(calendars, ahead, back))))
        return

    with open(outfile, "w") as fid:
        LOGGER.info("Writing calendars to: %s", outfile)
        fid.write("# -*- after-save-hook: cal-sync-push; -*-\n")
        fid.write("\n\n".join(dict.fromkeys(org_events(calendars, ahead, back))))
        fid.write("\n")


def write_addressbook(config, args):
    "Write Contacts to file"
    addresses = asyncio.run(get_resource(config, "addressbooks", args.force))
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
    parser.add_argument("-r", "--url", help="force direct download from url no auth")
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
