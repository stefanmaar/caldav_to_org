# -*- coding: utf-8 -*-
r"""
Convert Caldav to org-contacts
==============================
"""
# Author: Óscar Nájera
# License: GPL-3
# Inspired https://gist.github.com/tmalsburg/9747104

import dateutil.parser
import vobject  # type: ignore
from org_agenda import org


def get_properties(contact):
    "Extract all contact elements as properties"
    ignore = ["VERSION", "PRODID", "FN", "NOTE", "CATEGORIES"]

    for prop in contact.getChildren():

        name = prop.name
        value = prop.value
        # Special treatment for some fields:
        if prop.name in ignore or prop.name.startswith("X-"):
            continue

        if prop.name == "N":
            value = "%s;%s;%s;%s;%s" % (
                prop.value.family,
                prop.value.given,
                prop.value.additional,
                prop.value.prefix,
                prop.value.suffix,
            )

        if prop.name == "ADR":
            value = (
                prop.value.street,
                prop.value.code + " " + prop.value.city,
                prop.value.region,
                prop.value.country,
                prop.value.extended,
                prop.value.box,
            )
            value = ", ".join([x for x in value if x.strip() != ""])
            name = "ADDRESS"

        if prop.name == "REV":
            value = dateutil.parser.parse(prop.value)
            value = value.strftime("[%Y-%m-%d %a %H:%M]")

        if prop.name == "TEL":
            name = "PHONE"

        # Collect type attributes:
        attribs = ", ".join(prop.params.get("TYPE", []))
        if attribs:
            attribs = " (%s)" % attribs

        # Make sure that there are no newline chars left as that would
        # break org's property format:
        if isinstance(value, (list, tuple)):
            value = ", ".join(value)
        value = value.replace("\n", ", ")
        if value:
            yield name, value + attribs


class OrgContact(org.OrgEntry):
    "Contact representation in Org-mode"

    def __init__(self, contact):
        super().__init__(contact)
        self.property_parser = get_properties
        self.heading = contact.fn.value
        self.description = contact.getChildValue("note", "")
        self.dates = ""

    @property
    def tags(self):
        "Tags"
        return org.tags(self.entry.getChildValue("categories", []))


def org_contacts(addressbooks):
    "Iterate all addressbooks to generate contacts"
    for book in map(vobject.readComponents, addressbooks):
        for contact in book:
            yield str(OrgContact(contact))
