Exploring ScotRail Audio Clips using Ibis-Datasette
###################################################

:date: 2022-08-24 22:30
:slug: ibis-datasette-scotrail
:author: Jim Crist-Harif
:summary: Using ibis-datasette to explore a collection of ScotRail audio announcements

.. raw:: html

    <p>
    <em>
    Note: This blogpost is available as an interactive notebook
    <a class="reference external"
       href="https://gke.mybinder.org/v2/gh/jcrist/ibis-datasette/main?urlpath=/tree/Scotrail.ipynb"
    >here</a>.
    </em>
    </p>

|binder|

In the `previous post <{filename}/ibis-datasette.rst>`_ we introduced
`ibis-datasette`_. To recap:

- Datasette_  is a tool for publishing and exploring SQLite_ databases. Among
  other things, it exposes a UI and JSON API for querying a remote SQLite
  database.
- Ibis_ is a Python library that provides a consistent dataframe-like API for
  querying data using a number of SQL (and non-SQL) backends.
- Ibis-Datasette_ is a backend for Ibis that lets it interact with a datasette
  server just like it was a local SQLite database.

In this post, we'll use ``ibis`` and ``ibis-datasette`` to explore the
ScotRail_ datasette.

This datasette is super fun to play around with. It's composed of ~2400
different audioclips (and transcriptions) from Scottish train operator
ScotRail's automated station announcements.

If you haven't seen it, I encourage you to read Simon Willison's `excellent
blogpost <https://simonwillison.net/2022/Aug/21/scotrail/>`_ on putting this
datasette together, and some interesting queries to try (we'll be replicating
one of these below).

While you can use the `datasette UI <https://scotrail.datasette.io>`_ directly,
I wanted to use ``ibis`` and the full power of Python to explore and build some
interesting things.

---

First we start with some imports and initialization.

Here we:

- Import ``ibis`` and its ``_`` helper (more on this later)
- Enable interactive mode.
- We also tweak some ``pandas`` display options to better render wide columns.
  This makes the transcriptions below easier to read.

.. code-block:: python

    In [1]: import ibis
    ...: from ibis import _

    In [2]: ibis.options.interactive = True

    In [3]: import pandas as pd
    ...: pd.set_option('max_colwidth', 400)

Next we need to connect to the datasette. This is done by passing the full URL
to ``ibis.datasette.connect``:

.. code-block:: python

    In [4]: con = ibis.datasette.connect("https://scotrail.datasette.io/scotrail")

Once connected, we can start poking around.

The first thing I usually do when exploring a new dataset is examine the tables
and schemas.

.. code-block:: python

    In [5]: con.list_tables()
    Out[5]:
    ['announcements',
     'announcements_fts',
     'announcements_fts_config',
     'announcements_fts_data',
     'announcements_fts_docsize',
     'announcements_fts_idx']

    In [6]: con.tables.announcements.schema()
    Out[6]:
    ibis.Schema {
      File           string
      Transcription  string
      Category       string
      mp3            string
      Notes          string
      Timestamp      string
      NRE_ID         string
    }

    In [7]:  con.tables.announcements.head()
    Out[7]:
       File                              Transcription Category  ...                      Notes Timestamp NRE_ID
    0  0031            I am sorry to announce that the  Apology  ...
    1  0085          We are sorry to announce that the  Apology  ...  Most frequently used file
    2  1339              We are sorry to announce that  Apology  ...
    3  1488  we apologise for the inconvenience caused  Apology  ...
    4  1524                  Apologies to customers...  Apology  ...

    [5 rows x 7 columns]


The main table is ``announcements``, the most interesting columns of which are:

- ``Transcription``: a full transcription of the audio clip
- ``Category``: a category that the audio clip belongs to
- ``mp3``: a link to the audio clip, hosted on GitHub

Since we're going to be accessing this table a lot below, lets save it to a
shorter local variable name:

.. code-block:: python

    In [8]: t = con.tables.announcements

To get a better sense of the scale of data we're working with, lets take a
closer look at the ``Category`` column.

I want to know how many categories there are, and how the audio clips are
distributed across these categories.

To do this, we can use:

- ``.group_by("Category")`` to split the data into separate groups by ``Category``
- ``.count()`` to then count how many rows are in each category.
- ``.sort_by(ibis.desc("count"))`` to then sort the rows by ``count``,
  descending.

.. code-block:: python

    In [9]: category_counts = (
       ...:     t.group_by("Category")
       ...:      .count()
       ...:      .sort_by(ibis.desc("count"))
       ...: )
       ...:
       ...: category_counts
    Out[9]:
                        Category  count
    0                Destination   1271
    1                     Reason    421
    2                       Time    161
    3      Passenger information    153
    4                     Number    102
    5    Train operating company     76
    6       Platform information     67
    7                 Conjoining     66
    8                    Weather     30
    9                     Safety     15
    10           Train formation     14
    11             Special train     12
    12               Operational     10
    13                   Apology      8
    14          Fare information      7
    15               Platform ID      7
    16          Heritage Railway      6
    17              Number combo      4
    18                 Non-vocal      3
    19         Strathclyde metro      3
    20              Request stop      2
    21                   Station      1
    22  Train operating company       1


Here we can see there are 23 categories, with 90% of the audio clips falling
into the first 6. A few categories to highlight:

- ``Destination`` is a ScotRail stop
- ``Reason`` is a reason for a cancellation. These are fun to look through.
- ``Passenger information`` is a bit of miscellaneous. ("The train is ready to
  leave" for example)
- ``Number`` and ``Time`` are just clips of saying numbers and times
- ``Train operating company`` is the name of a train operating company
- ``Apology`` is the start of an apology for a service disruption ("I am sorry
  to announce that the" for example)

The ``Reason`` category is the most fun to look through. There are all sorts of
reasons a train might be cancelled, from "Sheep on the railway" to "A wartime
bomb near the railway".

One reoccuring reason is theft (err, "attempted theft") of various things. Lets
find all reasons involving "theft".

This can be done by using ``.filter()`` to filter rows based on a predicate.
Here we need two predicates:

- ``_.Category == "Reason"`` selects all rows that have a category of "Reason"
- ``_.Transcription.contains("theft")`` selects all rows with a transcription
  containing the string "theft"

.. code-block:: python

    In [10]: thefts = t.filter((_.Category == "Reason") & _.Transcription.contains("theft"))
        ...:
        ...: thefts
    Out[10]:
        File                                                             Transcription  ... Timestamp NRE_ID
    0   0969                Attempted theft of overhead line electrification equipment  ...
    1   0970  Attempted theft of overhead line electrification equipment earlier today  ...
    2   0971      Attempted theft of overhead line electrification equipment yesterday  ...
    3   0972                                      Attempted theft of railway equipment  ...
    4   0973                        Attempted theft of railway equipment earlier today  ...
    5   0974                            Attempted theft of railway equipment yesterday  ...
    6   0975                                      Attempted theft of signalling cables  ...
    7   0976                        Attempted theft of signalling cables earlier today  ...
    8   0977                            Attempted theft of signalling cables yesterday  ...
    9   0978                   Attempted theft of third rail electrification equipment  ...
    10  0979     Attempted theft of third rail electrification equipment earlier today  ...
    11  0980         Attempted theft of third rail electrification equipment yesterday  ...

    [12 rows x 7 columns]

All of these rows also include a link to an `mp3` file containing that clip. To
play a clip in a jupyter notebook, we can make use of `IPython.display.Audio`.
For example, lets play the first clip from above:

.. code-block:: python

    In [12]: from IPython.display import Audio
        ...:
        ...: mp3_url = thefts.limit(1).execute().mp3.iloc[0]
        ...:
        ...: Audio(mp3_url)

.. raw:: html

    <audio controls>
    <source src="https://github.com/matteason/scotrail-announcements-june-2022/raw/main/announcements/0969.mp3" type="audio/mpeg">
    Your browser does not support the audio element.
    </audio>


Generating a Random Apology
---------------------------

In `his blogpost <https://simonwillison.net/2022/Aug/21/scotrail/>`_ Simon
wrote up a SQL query for generating a Random apology by combining a few random
rows from different categories above. It generates surprisingly coherent
sentences, you can see the datasette version `here
<https://scotrail.datasette.io/scotrail/random_apology>`_.

If you're interested you can click "show" at the top to see the full SQL query
- it's readable, but a bit long.

I wanted to reproduce the same query using ``ibis``. Since ``ibis`` is just a
Python library, you can make use of things like functions to abstract away some
of the repetitiveness in the SQL query above.

Here's what I came up with:

.. code-block:: python

    In [12]: def random(category):
        ...:     """Select a random row from a given category"""
        ...:     return (
        ...:         t.filter(_.Category == category)
        ...:          .sort_by(ibis.random())
        ...:          .select("Transcription", "mp3")
        ...:          .limit(1)
        ...:     )
        ...:
        ...: def phrase(text):
        ...:     """Select a row with a specific transcription"""
        ...:     return (
        ...:         t.filter(_.Transcription == text)
        ...:          .select("Transcription", "mp3")
        ...:          .limit(1)
        ...:     )
        ...:
        ...: query = ibis.union(
        ...:     random("Apology"),
        ...:     random("Train operating company"),
        ...:     random("Destination"),
        ...:     phrase("has been cancelled"),
        ...:     phrase("due to"),
        ...:     random("Reason"),
        ...: )

Since the query selects random rows, if you run the cell below multiple times,
you should see different results every time:

.. code-block:: python

    In [13]: query.execute()
    Out[13]:
                         Transcription                                                                                            mp3
    0  I am sorry to announce that the  https://github.com/matteason/scotrail-announcements-june-2022/raw/main/announcements/1529.mp3
    1              Southeastern Trains  https://github.com/matteason/scotrail-announcements-june-2022/raw/main/announcements/0201.mp3
    2                          Dawlish  https://github.com/matteason/scotrail-announcements-june-2022/raw/main/announcements/0702.mp3
    3               has been cancelled  https://github.com/matteason/scotrail-announcements-june-2022/raw/main/announcements/0340.mp3
    4                           due to  https://github.com/matteason/scotrail-announcements-june-2022/raw/main/announcements/1528.mp3
    5    A person being hit by a train  https://github.com/matteason/scotrail-announcements-june-2022/raw/main/announcements/0834.mp3

If we wanted to do all computation in the backend, we could use
``group_concat`` (`docs
<https://www.sqlite.org/lang_aggfunc.html#group_concat>`_) to then concatenate
the Transcription rows together, returning a single string:

.. code-block:: python

    In [14]: random_apology = query.Transcription.group_concat(" ")
        ...:
        ...: random_apology
    Out[14]: 'we apologise for the inconvenience caused East Midlands Cartsdyke has
    been cancelled due to A train not stopping in the correct position at a station'

Note that the full query above is translated to SQL and executed on the
``datasette`` server, no computation is happening locally.

If you want to see the generated SQL, you can use the ``ibis.show_sql``
function. It's much longer than the Python code that generated it:

.. code-block:: python

    In [15]: ibis.show_sql(random_apology)
    WITH anon_1 AS (
      SELECT
        t1."Transcription" AS "Transcription",
        t1.mp3 AS mp3
      FROM (
        SELECT
          t2."File" AS "File",
          t2."Transcription" AS "Transcription",
          t2."Category" AS "Category",
          t2.mp3 AS mp3,
          t2."Notes" AS "Notes",
          t2."Timestamp" AS "Timestamp",
          t2."NRE_ID" AS "NRE_ID"
        FROM main.announcements AS t2
        WHERE
          t2."Category" = 'Apology'
        ORDER BY
          RANDOM()
      ) AS t1
      LIMIT 1
      OFFSET 0
    ), anon_2 AS (
      SELECT
        t1."Transcription" AS "Transcription",
        t1.mp3 AS mp3
      FROM (
        SELECT
          t2."File" AS "File",
          t2."Transcription" AS "Transcription",
          t2."Category" AS "Category",
          t2.mp3 AS mp3,
          t2."Notes" AS "Notes",
          t2."Timestamp" AS "Timestamp",
          t2."NRE_ID" AS "NRE_ID"
        FROM main.announcements AS t2
        WHERE
          t2."Category" = 'Train operating company'
        ORDER BY
          RANDOM()
      ) AS t1
      LIMIT 1
      OFFSET 0
    ), anon_3 AS (
      SELECT
        t1."Transcription" AS "Transcription",
        t1.mp3 AS mp3
      FROM (
        SELECT
          t2."File" AS "File",
          t2."Transcription" AS "Transcription",
          t2."Category" AS "Category",
          t2.mp3 AS mp3,
          t2."Notes" AS "Notes",
          t2."Timestamp" AS "Timestamp",
          t2."NRE_ID" AS "NRE_ID"
        FROM main.announcements AS t2
        WHERE
          t2."Category" = 'Destination'
        ORDER BY
          RANDOM()
      ) AS t1
      LIMIT 1
      OFFSET 0
    ), anon_4 AS (
      SELECT
        t1."Transcription" AS "Transcription",
        t1.mp3 AS mp3
      FROM (
        SELECT
          t2."File" AS "File",
          t2."Transcription" AS "Transcription",
          t2."Category" AS "Category",
          t2.mp3 AS mp3,
          t2."Notes" AS "Notes",
          t2."Timestamp" AS "Timestamp",
          t2."NRE_ID" AS "NRE_ID"
        FROM main.announcements AS t2
        WHERE
          t2."Transcription" = 'has been cancelled'
      ) AS t1
      LIMIT 1
      OFFSET 0
    ), anon_5 AS (
      SELECT
        t1."Transcription" AS "Transcription",
        t1.mp3 AS mp3
      FROM (
        SELECT
          t2."File" AS "File",
          t2."Transcription" AS "Transcription",
          t2."Category" AS "Category",
          t2.mp3 AS mp3,
          t2."Notes" AS "Notes",
          t2."Timestamp" AS "Timestamp",
          t2."NRE_ID" AS "NRE_ID"
        FROM main.announcements AS t2
        WHERE
          t2."Transcription" = 'due to'
      ) AS t1
      LIMIT 1
      OFFSET 0
    ), anon_6 AS (
      SELECT
        t1."Transcription" AS "Transcription",
        t1.mp3 AS mp3
      FROM (
        SELECT
          t2."File" AS "File",
          t2."Transcription" AS "Transcription",
          t2."Category" AS "Category",
          t2.mp3 AS mp3,
          t2."Notes" AS "Notes",
          t2."Timestamp" AS "Timestamp",
          t2."NRE_ID" AS "NRE_ID"
        FROM main.announcements AS t2
        WHERE
          t2."Category" = 'Reason'
        ORDER BY
          RANDOM()
      ) AS t1
      LIMIT 1
      OFFSET 0
    )
    SELECT
      GROUP_CONCAT(t0."Transcription", ' ') AS tmp
    FROM (
      SELECT
        anon_1."Transcription" AS "Transcription",
        anon_1.mp3 AS mp3
      FROM anon_1
      UNION ALL
      SELECT
        anon_2."Transcription" AS "Transcription",
        anon_2.mp3 AS mp3
      FROM anon_2
      UNION ALL
      SELECT
        anon_3."Transcription" AS "Transcription",
        anon_3.mp3 AS mp3
      FROM anon_3
      UNION ALL
      SELECT
        anon_4."Transcription" AS "Transcription",
        anon_4.mp3 AS mp3
      FROM anon_4
      UNION ALL
      SELECT
        anon_5."Transcription" AS "Transcription",
        anon_5.mp3 AS mp3
      FROM anon_5
      UNION ALL
      SELECT
        anon_6."Transcription" AS "Transcription",
        anon_6.mp3 AS mp3
      FROM anon_6
    ) AS t0

However, we're only using ``ibis`` to push the bulk of the computation to the
backend. We don't need to handle *everything* in SQL, only enough to reduce the
size of the results to something reasonable to return from the ``datasette``
server.

We also have access to the full Python ecosystem to process results. This lets
us do some things that wouldn't be possible in SQL alone, like concatenating
``mp3`` files :).

A "Random Apology" Button
-------------------------

The ipywidgets_ library provides support for building simple UIs in Python,
with the rendering handled by the notebook. This is nice for me, as I am *not*
a web engineer - I'm a novice at best at javascript/html. However, I do know
how to write Python.

Below we hack together a quick UI with ``ipywidgets`` to make a button for
generating a random apology, complete with a merged ``mp3`` file so you can
listen to your work. You don't really need to understand this code, it has
nothing to do with ``ibis`` or ``ibis-datasette`` itself.

Clicking the button will pull generate a new random apology, download and merge
the mp3 files, and display both the apology sentence and merged mp3.

Obviously this can't run for real in a static blogpost (it's most
interesting in the interactive notebook on mybinder_). To work around
that, we include a single generated audio clip below.

.. code-block:: python

    In [16]: import tempfile
        ...: import os
        ...: import pydub
        ...: import httpx
        ...: import ipywidgets
        ...: from IPython.display import Audio, display
        ...:
        ...: output = ipywidgets.Output()
        ...: button = ipywidgets.Button(description='Random Apology', icon="repeat")
        ...: UI = ipywidgets.VBox([button, output])
        ...:
        ...:
        ...: def concatenate_mp3s(urls: list[str]) -> bytes:
        ...:     with httpx.Client(follow_redirects=True) as client, tempfile.TemporaryDirectory() as tempdir:
        ...:         output = None
        ...:         for i, url in enumerate(urls):
        ...:             path = os.path.join(tempdir, f"part{i}.mp3")
        ...:             with open(path, "wb") as f:
        ...:                 resp = client.get(url)
        ...:                 resp.raise_for_status()
        ...:                 f.write(resp.content)
        ...:             part = pydub.AudioSegment.from_mp3(path)
        ...:             if output is None:
        ...:                 output = part
        ...:             else:
        ...:                 output = output + part
        ...:         out_path = os.path.join(tempdir, "output.mp3")
        ...:         output.export(out_path, format="mp3")
        ...:         with open(out_path, "rb") as f:
        ...:             return f.read()
        ...:
        ...:
        ...: @button.on_click
        ...: def on_click(*args):
        ...:     output.clear_output()
        ...:     result = query.execute()
        ...:     msg = " ".join(result.Transcription)
        ...:     mp3 = concatenate_mp3s(result.mp3)
        ...:     with output:
        ...:         print(msg)
        ...:         display(Audio(mp3))
        ...:
        ...:
        ...: UI

.. code-block:: text

    I am sorry to announce that the Midland Mainline Turbostar service from
    Mitcham Eastfields has been cancelled due to The train conductor being
    taken ill

.. raw:: html

    <audio controls>
    <source src="/images/scotrail-madlib.mp3" type="audio/mpeg">
    Your browser does not support the audio element.
    </audio>

Review
------

``datasette`` makes it easier to publish accessible open data on the web, with
a UI exposed for writing SQL queries. However, not everyone is extremely SQL
literate (myself included). ``ibis`` and ``ibis-datasette`` let Python
programmers access this same data resource, but through a familiar
dataframe-like interface.

Interested in ``ibis`` or ``ibis-datasette``? Please feel free to reach out on
`github <https://github.com/jcrist>`_ or `twitter
<https://twitter.com/jcristharif>`_.


.. _ScotRail: https://scotrail.datasette.io/
.. _ibis-datasette: https://github.com/jcrist/ibis-datasette
.. _datasette: https://datasette.io
.. _sqlite: https://sqlite.org
.. _ibis: https://ibis-project.org
.. _ipywidgets: https://ipywidgets.readthedocs.io
.. _mybinder: https://gke.mybinder.org/v2/gh/jcrist/ibis-datasette/main?urlpath=/tree/Scotrail.ipynb

.. |binder| image:: https://mybinder.org/badge_logo.svg
   :target: https://gke.mybinder.org/v2/gh/jcrist/ibis-datasette/main?urlpath=/tree/Scotrail.ipynb

