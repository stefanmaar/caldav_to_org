======================
Orgmode Agenda utility
======================


.. image:: https://gitlab.com/Titan-C/org-mode-agenda/badges/master/pipeline.svg
    :target: https://gitlab.com/Titan-C/org-mode-agenda/-/commits/master
.. image:: https://img.shields.io/badge/License-GPL%20v3-blue.svg
    :target: https://www.gnu.org/licenses/gpl-3.0


This python script downloads your caldav calendars and generates and org
agenda file.

1 Install
---------

.. code:: bash

    python setup.py develop

2 Configuration
---------------

Edit the config file ``~/.calendars.conf``. The ``DEFAULT`` section configures
where to write the output and days ahead and back from execution date.

Then every new section is a calendar file. You can name sections as you
prefer. This names have no influence on the output file.

.. code:: bash

    [DEFAULT]
    outfile=~/org/caldav.org
    ahead=90 # Days ahead from today
    back=28 # Days in the past

    [work] # Calendar name
    user = on
    passwordstore=Correos/mx.tribe29.com
    # url for direct download of ics file
    url=https://website.com/dav/calendar/personal?export

3 Contributions
---------------

You can kindly tip me for this project

Stellar
    GDPTOFND6HSE5AVHPRXOCJFOA6NPFB65JAEWKTN23EBUGBB2AU4PLIBD

4 License
---------

::

    org-mode-agenda
    Copyright (C) 2020  Óscar Nájera

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
