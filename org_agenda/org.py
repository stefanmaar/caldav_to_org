# -*- coding: utf-8 -*-
r"""
Convert Caldav to org-contacts
==============================
"""
# Author: Óscar Nájera
# License: GPL-3
# Inspired https://gist.github.com/tmalsburg/9747104


def tags(tag_list):
    "Tags"

    if _tags := ":".join(tag_list).replace("-", "_"):
        return f"  :{_tags}:"
    return ""


def string(node):
    "string representation of org entry"
    return (
        f"* {node.heading}{node.tags}\n"
        f"{node.properties}{node.dates}{node.description}"
    ).strip()


class OrgEntry:
    "Org-Mode basic entry"

    def __init__(self, entry):
        self.entry = entry
        self.property_parser = lambda x: []

    @property
    def properties(self):
        "Property box"
        props = "\n".join(
            ":%s: %s" % (k, v) for k, v in self.property_parser(self.entry)
        )
        return f""":PROPERTIES:\n{props}\n:END:\n""" if props else ""

    def __str__(self):
        return string(self)
