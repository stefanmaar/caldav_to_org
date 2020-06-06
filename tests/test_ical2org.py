import os
import time
from contextlib import contextmanager

import pytest
from freezegun import freeze_time

from icalendar import Calendar
from org_agenda import ical2org

@contextmanager
def on_date(date, timezone):
    """Set the time and timezone for the test"""

    os.environ['TZ'] = timezone
    time.tzset()
    with freeze_time(date):
        yield
    os.environ.pop('TZ')
    time.tzset()

@pytest.mark.parametrize(
    "ics, result",
    [
        pytest.param(
            """BEGIN:VCALENDAR
BEGIN:VEVENT
UID:first
SUMMARY:Feed the dragons
LOCATION:forest
DTSTART;TZID="Europe/Berlin":20200319T103000
DTEND;TZID="Europe/Berlin":20200319T113000
DESCRIPTION:take some meat
CATEGORIES:pets,dragons
CATEGORIES:shopping
END:VEVENT
END:VCALENDAR""",
            """* Feed the dragons  :pets:dragons:shopping:
:PROPERTIES:
:LOCATION: forest
:ID: first
:END:
  <2020-03-19 Thu 10:30>--<2020-03-19 Thu 11:30>
take some meat""",
            id="simple event",
        ),
        pytest.param(
            """BEGIN:VCALENDAR
BEGIN:VEVENT
DTSTART:20200319T173000Z
DTEND:20200319T181500Z
UID:second
DESCRIPTION: Search for big animals
  that are on the open
LOCATION:big forest
SUMMARY:Go hunting
BEGIN:VALARM
ACTION:DISPLAY
TRIGGER;RELATED=START:-PT15M
DESCRIPTION:Reminder
END:VALARM
END:VEVENT
END:VCALENDAR""",
            """* Go hunting
:PROPERTIES:
:LOCATION: big forest
:ID: second
:APPT_WARNTIME: 15
:END:
  <2020-03-19 Thu 18:30>--<2020-03-19 Thu 19:15>
 Search for big animals that are on the open""",
            id="Multiline description",
        ),
        pytest.param(
            """BEGIN:VEVENT
UID:fullday
SUMMARY:Home day
DTSTART;VALUE=DATE:20200312
DTEND;VALUE=DATE:20200313
CATEGORIES:cleanup
END:VEVENT""",
            """* Home day  :cleanup:
:PROPERTIES:
:ID: fullday
:END:
  <2020-03-12 Thu>""",
            id="Full day",
        ),
        pytest.param(
            """BEGIN:VEVENT
UID:forthofmonth
DTSTART;TZID=Europe/Berlin:20200125T190000
DTEND;TZID=Europe/Berlin:20200125T210000
SUMMARY:Monthly meeting
RRULE:FREQ=MONTHLY;BYDAY=WE;BYSETPOS=4
EXDATE;TZID=Europe/Berlin:20200325T190000
END:VEVENT""",
            """* Monthly meeting
:PROPERTIES:
:ID: forthofmonth
:RRULE: FREQ=MONTHLY;BYDAY=WE;BYSETPOS=4
:END:
  <2020-02-26 Wed 19:00>--<2020-02-26 Wed 21:00>
  <2020-04-22 Wed 19:00>--<2020-04-22 Wed 21:00>""",
            id="repetitions 4th wed of month with exception",
        ),
        pytest.param(
            """BEGIN:VEVENT
DTSTAMP:20191226T190839Z
UID:J480MNXCKM88LL7UQ2ITQX
SUMMARY:travel
LOCATION:train
DTSTART;TZID=Europe/Berlin:20181206T190000
DURATION:PT3H
RRULE:FREQ=WEEKLY;WKST=SU;BYDAY=TH
BEGIN:VALARM
TRIGGER:-PT60M
END:VALARM
END:VEVENT
""",
            """* travel
:PROPERTIES:
:LOCATION: train
:ID: J480MNXCKM88LL7UQ2ITQX
:RRULE: FREQ=WEEKLY;BYDAY=TH;WKST=SU
:APPT_WARNTIME: 60
:END:
  <2020-02-20 Thu 19:00>--<2020-02-20 Thu 22:00>
  <2020-02-27 Thu 19:00>--<2020-02-27 Thu 22:00>
  <2020-03-05 Thu 19:00>--<2020-03-05 Thu 22:00>
  <2020-03-12 Thu 19:00>--<2020-03-12 Thu 22:00>
  <2020-03-19 Thu 19:00>--<2020-03-19 Thu 22:00>
  <2020-03-26 Thu 19:00>--<2020-03-26 Thu 22:00>
  <2020-04-02 Thu 19:00>--<2020-04-02 Thu 22:00>
  <2020-04-09 Thu 19:00>--<2020-04-09 Thu 22:00>
  <2020-04-16 Thu 19:00>--<2020-04-16 Thu 22:00>
  <2020-04-23 Thu 19:00>--<2020-04-23 Thu 22:00>""",
            id="duration and weekly repeat",
        ),
        pytest.param("""BEGIN:VCALENDAR
BEGIN:VEVENT
UID:835f0339-d824-42f4-9e1e-82b45229d75d
DTSTART;TZID=Europe/Berlin:20200419T130000
DTEND;TZID=Europe/Berlin:20200419T140000
SUMMARY:Crisis
RRULE:FREQ=DAILY;UNTIL=20200426T000000
END:VEVENT
BEGIN:VEVENT
UID:835f0339-d824-42f4-9e1e-82b45229d75d
DTSTART;TZID=Europe/Berlin:20200422T170000
DTEND;TZID=Europe/Berlin:20200422T190000
SUMMARY:Crisis Management
LOCATION:Office
RECURRENCE-ID;TZID=Europe/Berlin:20200422T130000
END:VEVENT
BEGIN:VEVENT
UID:835f0339-d824-42f4-9e1e-82b45229d75d
DTSTART;TZID=Europe/Berlin:20200424T210000
DTEND;TZID=Europe/Berlin:20200424T220000
SUMMARY:Crisis Breakdown
LOCATION:Volcano
RECURRENCE-ID;TZID=Europe/Berlin:20200424T130000
END:VEVENT
BEGIN:VEVENT
UID:e5a638dc-3125-454b-856d-60d3015bed2e
DTSTART;TZID=Europe/Berlin:20200419T120010
DTEND;TZID=Europe/Berlin:20200419T130010
SUMMARY:Daily
RRULE:FREQ=WEEKLY;COUNT=5;BYDAY=MO,TU,WE,TH,FR
END:VEVENT
BEGIN:VEVENT
UID:e5a638dc-3125-454b-856d-60d3015bed2e
DTSTART;TZID=Europe/Berlin:20200421T150000
DTEND;TZID=Europe/Berlin:20200421T160000
SUMMARY:Daily later
RECURRENCE-ID;TZID=Europe/Berlin:20200421T120010
END:VEVENT
END:VCALENDAR""","""* Crisis
:PROPERTIES:
:ID: 835f0339-d824-42f4-9e1e-82b45229d75d
:RRULE: FREQ=DAILY;UNTIL=20200425T220000Z
:END:
  <2020-04-19 Sun 13:00>--<2020-04-19 Sun 14:00>
  <2020-04-20 Mon 13:00>--<2020-04-20 Mon 14:00>
  <2020-04-21 Tue 13:00>--<2020-04-21 Tue 14:00>
  <2020-04-23 Thu 13:00>--<2020-04-23 Thu 14:00>
  <2020-04-25 Sat 13:00>--<2020-04-25 Sat 14:00>

* Crisis Management
:PROPERTIES:
:LOCATION: Office
:ID: 835f0339-d824-42f4-9e1e-82b45229d75d
:END:
  <2020-04-22 Wed 17:00>--<2020-04-22 Wed 19:00>

* Crisis Breakdown
:PROPERTIES:
:LOCATION: Volcano
:ID: 835f0339-d824-42f4-9e1e-82b45229d75d
:END:
  <2020-04-24 Fri 21:00>--<2020-04-24 Fri 22:00>

* Daily
:PROPERTIES:
:ID: e5a638dc-3125-454b-856d-60d3015bed2e
:RRULE: FREQ=WEEKLY;COUNT=5;BYDAY=MO,TU,WE,TH,FR
:END:
  <2020-04-20 Mon 12:00>--<2020-04-20 Mon 13:00>
  <2020-04-22 Wed 12:00>--<2020-04-22 Wed 13:00>
  <2020-04-23 Thu 12:00>--<2020-04-23 Thu 13:00>
  <2020-04-24 Fri 12:00>--<2020-04-24 Fri 13:00>

* Daily later
:PROPERTIES:
:ID: e5a638dc-3125-454b-856d-60d3015bed2e
:END:
  <2020-04-21 Tue 15:00>--<2020-04-21 Tue 16:00>""",id="many changes")
    ],
)
@on_date("2020-03-19", "Europe/Berlin")
def test_conversion(ics, result):
    events = "\n\n".join(ical2org.org_events([ics], 40, 30))
    print(events)
    assert events == result
