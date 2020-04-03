# -*- coding: utf-8 -*-
r"""
Convert Caldav to org-contacts
==============================
"""
# Author: Óscar Nájera
# License: GPL-3
# Inspired https://gist.github.com/tmalsburg/9747104

import dateutil.parser
import vobject


def get_properties(contact):
    for p in contact.getChildren():

        name = p.name
        value = p.value
        # Special treatment for some fields:
        if p.name in [
            "VERSION",
            "PRODID",
            "FN",
            "NOTE",
            "CATEGORIES",
        ] or p.name.startswith("X-"):
            continue

        if p.name == "N":
            value = "%s;%s;%s;%s;%s" % (
                p.value.family,
                p.value.given,
                p.value.additional,
                p.value.prefix,
                p.value.suffix,
            )

        if p.name == "ADR":
            # TODO Make the formatting sensitive to X-ABADR:
            value = (
                p.value.street,
                p.value.code + " " + p.value.city,
                p.value.region,
                p.value.country,
                p.value.extended,
                p.value.box,
            )
            value = ", ".join([x for x in value if x.strip() != ""])
            name = "ADDRESS"

        if p.name == "REV":
            value = dateutil.parser.parse(p.value)
            value = value.strftime("[%Y-%m-%d %a %H:%M]")

        if p.name == "TEL":
            name = "PHONE"

        # Collect type attributes:
        attribs = ", ".join(p.params.get("TYPE", []))
        if attribs:
            attribs = " (%s)" % attribs

        # Make sure that there are no newline chars left as that would
        # break org's property format:
        if isinstance(value, (list, tuple)):
            value = ", ".join(value)
        value = value.replace("\n", ", ")
        if value:
            yield name, value + attribs


class OrgContact:
    def __init__(self, contact):
        self.name = contact.fn.value
        self.contact = contact
        self.note = contact.getChildValue("note", "")

    @property
    def tags(self):
        "Tags"
        tags = self.contact.getChildValue("categories", [])
        if not isinstance(tags, list):
            tags = [tags]

        tags = ":".join(tags)

        if tags:
            return f"  :{tags}:"
        return ""

    @property
    def properties(self):
        "Property box"
        props = "\n".join(":%s: %s" % (k, v) for k, v in get_properties(self.contact))
        return f""":PROPERTIES:\n{props}\n:END:\n""" if props else ""

    def __str__(self):
        return f"* {self.name}{self.tags}\n{self.properties}{self.note}".strip()


def org_contacts(addressbooks):
    for book in map(vobject.readComponents, addressbooks):
        for contact in book:
            yield str(OrgContact(contact))
