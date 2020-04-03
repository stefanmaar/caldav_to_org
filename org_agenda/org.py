# -*- coding: utf-8 -*-
r"""
Convert Caldav to org-contacts
==============================
"""
# Author: Óscar Nájera
# License: GPL-3
# Inspired https://gist.github.com/tmalsburg/9747104

import types


def tags(tag_list, process=lambda x: x):
    "Tags"
    if not isinstance(tag_list, (list, types.GeneratorType)):
        tag_list = [tag_list]

    _tags = ":".join(map(process, tag_list))

    if _tags:
        return f"  :{_tags}:"
    return ""


class OrgNode:
    def __init__(self, entry):
        self.entry = entry

    @property
    def properties(self):
        "Property box"
        props = "\n".join(
            ":%s: %s" % (k, v) for k, v in self.property_parser(self.entry)
        )
        return f""":PROPERTIES:\n{props}\n:END:\n""" if props else ""

    def __str__(self):
        return (
            f"* {self.heading}{self.tags}\n"
            f"{self.properties}{self.dates}{self.description}"
        ).strip()
