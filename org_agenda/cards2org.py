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
from org_agenda import org


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


class OrgContact(org.OrgNode):
    def __init__(self, contact):
        super().__init__(contact)
        self.property_parser = get_properties
        self.heading = contact.fn.value
        self.description = contact.getChildValue("note", "")
        self.dates = ""

    @property
    def tags(self):
        "Tags"
        return org.tags(self.contact.getChildValue("categories", []))


def org_contacts(addressbooks):
    for book in map(vobject.readComponents, addressbooks):
        for contact in book:
            yield str(OrgContact(contact))
