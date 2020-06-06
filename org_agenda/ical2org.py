# -*- coding: utf-8 -*-
r"""
Convert icalendar elements into org-mode elements
=================================================
"""
# Created: Thu Mar 19 12:48:59 2020
# Author: Óscar Nájera
# License: GPL-3

from datetime import datetime, timedelta
from dateutil import tz
from dateutil.rrule import rrulestr
from icalendar import Calendar  # type: ignore
from pytz import utc
from tzlocal import get_localzone  # type: ignore
from org_agenda import org

# inspiration from
# https://www.nylas.com/blog/calendar-events-rrules/


def orgdatetime(datestamp, time_zone, time=True):
    """Timezone aware datetime to YYYY-MM-DD DayofWeek HH:MM str in localtime.
    """
    hours = " %H:%M" if time else ""
    str_format = f"<%Y-%m-%d %a{hours}>"

    return datestamp.astimezone(time_zone).strftime(str_format)


def org_interval(start, duration, time_zone):
    "Write org interval"
    if duration.total_seconds() % 86400 == 0:
        datestr = "  {}".format(orgdatetime(start, time_zone, False))
        if duration.total_seconds() / 86400 > 1:
            datestr += "--{}".format(
                orgdatetime(start + duration - timedelta(seconds=1), time_zone, False)
            )
        return datestr + "\n"

    return "  {}--{}\n".format(
        orgdatetime(start, time_zone), orgdatetime(start + duration, time_zone),
    )


def put_tz(date_time):
    "Given date or datetime enforce transformation to localtime"
    if not hasattr(date_time, "hour"):
        return datetime(
            year=date_time.year,
            month=date_time.month,
            day=date_time.day,
            tzinfo=tz.tzlocal(),
        )
    return date_time.astimezone(tz.tzlocal())


def get_properties(event):
    "Extract relevant properties"
    properties = ("LOCATION", "UID")
    for prop in properties:
        value = event.get(prop, "").strip()
        if value:
            if prop == "UID":
                prop = "ID"
            yield prop, value

    if "RRULE" in event:
        yield "RRULE", rrule_cleanup(event["RRULE"])


    for comp in event.subcomponents:
        if comp.name == "VALARM":
            trigger = int(-1 * comp["TRIGGER"].dt.total_seconds() / 60)
            yield "APPT_WARNTIME", str(trigger)


def rrule_cleanup(rrule_conf):
    "Repetition rule needs to respect some constrains, return clean string"
    until = rrule_conf.get("UNTIL")
    if until:
        rrule_conf["UNTIL"][0] = until[0].astimezone(tz.UTC)

    return rrule_conf.to_ical().decode("utf-8")


def rrule(org_event, exceptions=None):
    "Create event repetition rule"

    rule = rrulestr(
        rrule_cleanup(org_event.entry["RRULE"]),
        dtstart=org_event.dtstart,
        forceset=True,
    )

    exdates = org_event.entry.get("EXDATE", [])
    for dates in (exdates,) if not isinstance(exdates, list) else exdates:
        for date in dates.dts:
            rule.exdate(put_tz(date.dt))

    if exceptions:
        for date in exceptions:
            new_datetime = put_tz(date.dt).replace(
                hour=org_event.dtstart.hour, minute=org_event.dtstart.minute
            )
            rule.exdate(new_datetime)

    return rule


class OrgEvent(org.OrgEntry):
    """Documentation for OrgEntry"""

    def __init__(self, event):
        super().__init__(event)
        self.property_parser = get_properties
        self.heading = event["SUMMARY"]
        self.dtstart = put_tz(event["DTSTART"].dt)
        if "DTEND" in event:
            self.dtend = put_tz(event["DTEND"].dt)
            self.duration = self.dtend - self.dtstart
        else:
            self.duration = event["DURATION"].dt

        self.dates = ""

        self.description = (
            event["DESCRIPTION"].replace(" \n", "\n") if "DESCRIPTION" in event else ""
        )

    @property
    def tags(self):
        "Tags"
        return org.tags(
            self.entry.get("CATEGORIES", []),
            lambda x: x.to_ical().decode("utf-8").replace(" ", "-").replace(",", ":"),
        )

    def date_block(self, start, end, exceptions=None):
        "Evaluate which active dates the event has"

        if "RRULE" in self.entry:
            rule = rrule(self, exceptions)
            self.dates = "".join(
                org_interval(event_start, self.duration, get_localzone())
                for event_start in rule.between(after=start, before=end)
            )

        elif self.dtstart < end and self.dtstart > start:
            self.dates = org_interval(self.dtstart, self.duration, get_localzone())

        return self.dates


def changev(evlist, start, end):
    "Clean repeating occurrences that have a specific event change"
    mods = [e.entry.get("RECURRENCE-ID") for e in evlist]

    if len(evlist) == 1 or None not in mods:
        return evlist

    base_ind = mods.index(None)
    mods.pop(base_ind)

    base = evlist.pop(base_ind)
    base.date_block(start, end, mods)

    return ([base] if base.dates else []) + evlist


def org_calendar(ical, start, end):
    "Return calendar time relevant calendar events"
    events = (OrgEvent(entry) for entry in ical.walk() if entry.name == "VEVENT")
    regular_events = {}
    for event in events:
        if event.date_block(start, end):
            regular_events.setdefault(event.entry.get("UID"), []).append(event)

    for evlist in regular_events.values():
        yield from map(str, changev(evlist, start, end))


def org_events(calendars, ahead, back):
    "Iterator of all events in calendars from [today-back;today+ahead]"

    now = datetime.now(utc)
    start = now - timedelta(back)
    end = now + timedelta(ahead)

    for ical in map(Calendar.from_ical, calendars):
        yield from org_calendar(ical, start, end)
