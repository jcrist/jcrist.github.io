Ibis-Datasette
##############

:date: 2022-08-18 8:15
:slug: ibis-datasette
:author: Jim Crist-Harif
:summary: An ibis backend for querying a datasette server

.. raw:: html

    <img title="ibis loves datasette" class="align-center" src="/images/ibis-loves-datasette.png" style="width: 60%;" />

Datasette
---------

Datasette_ is an *excellent* tool for exploring and publishing data. Given an
existing SQLite_ database, it provides:

- A `nice web UI <https://global-power-plants.datasettes.com>`_ for exploring
  the dataset
- A flexible `JSON API <https://docs.datasette.io/en/stable/json_api.html>`_
  for querying the dataset using SQL (``SELECT`` statements only)
- Tooling for `publishing <https://docs.datasette.io/en/stable/publish.html>`_
  that data on a number of common cloud platforms.

It also has a `large ecosystem of plugins
<https://docs.datasette.io/en/stable/plugins.html>`_ supporting everything from
adding maps and visualizations, to extending SQLite with custom SQL functions.

For more information, I encourage you to `watch this intro video
<https://www.youtube.com/watch?v=7kDFBnXaw-c>`_. Or just start poking around
the `examples <datasette.io/examples>`_. The UI lends itself well to
self-guided exploration.

Ibis
----

At my `new day job <https://voltrondata.com>`_ I work on another SQL-adjacent
tool called Ibis_. Ibis provides a consistent dataframe-like API for querying
data using a number of SQL (and non-SQL) backends.

It looks like this:

.. code-block:: python

    In [1]: import ibis

    In [2]: ibis.options.interactive = True  # enable interactive mode

    In [3]: con = ibis.sqlite.connect("legislators.db")  # connect to a database

    In [4]: legislators = con.tables["legislators"]  # access tables

    In [5]: legislators.groupby("bio_gender").count()  # query using a dataframe-like API
    Out[5]:
      bio_gender  count
    0          F    399
    1          M  12195

For users less familiar with SQL (like myself), having a dataframe-like API can
enable better usage of existing data tools. Without Ibis I'd be more prone to
writing simple ``SELECT`` statements only to extract the data I cared about,
then analyze it locally using a more familiar tool like ``pandas``. With
``ibis`` I can run more of my queries in the backing database itself, improving
execution time and reducing data transfer.

Datasette & Ibis
----------------

Ibis supports a `large number of backends and operations
<https://ibis-project.org/docs/3.1.0/backends/support_matrix/>`_. As such, its
internals can get a bit *complicated*. To help onboard myself to the project, I
decided to write a new tiny backend linking Ibis and Datasette. This is
something I've wanted for a while - I'm more comfortable in a terminal than a
web UI, but I wanted to explore all the `interesting open datasets
<https://datasette.io/examples>`_ Simon and team have put together.

The project is called ``ibis-datasette`` (`repo
<https://github.com/jcrist/ibis-datasette>`_). It can be installed using
``pip``:

.. code-block:: term

    $ pip install ibis-datasette

Using it, you can connect ``ibis`` to any ``datasette`` server by passing in
the full URL. For example, here we connect to the `congress-legislators`_
datasette demo, and run the same query as we did above:

.. code-block:: python

    In [1]: import ibis

    In [2]: ibis.options.interactive = True

    In [3]: con = ibis.datasette.connect(
       ...:    "https://congress-legislators.datasettes.com/legislators"
       ...: )

    In [4]: legislators = con.tables["legislators"]

    In [5]: legislators.groupby("bio_gender").count()
    Out[5]:
      bio_gender  count
    0          F    399
    1          M  12195

Even though we're executing on a different backend with a different protocol,
the user-facing code is the same, only the ``connect`` call is different.

Of course ``ibis`` can run more complicated queries.

For example, here we learn that `Jeannette Rankin
<https://en.wikipedia.org/wiki/Jeannette_Rankin>`_ was the first female US
representative, elected in 1917 in Montana.

.. code-block:: python

    In [6]: terms = con.tables["legislator_terms"]

    In [7]: first_female_rep = (
       ...:    legislators
       ...:    .join(terms, legislators.id == terms.legislator_id)
       ...:    .filter(lambda _: _.bio_gender == "F")
       ...:    .select("name", "state", "start")
       ...:    .sort_by("start")
       ...:    .limit(1)
       ...: )

    In [8]: first_female_rep
    Out[8]:
                   name state       start
    0  Jeannette Rankin    MT  1917-04-02

For an even more complicated query, here we compute the percentage of female US
representatives per decade, filtering out the ~140 years of no representation:

.. code-block:: python

    In [9]: percent_female_by_decade = (
       ...:     legislators
       ...:     .join(terms, legislators.id == terms.legislator_id)
       ...:     .select("bio_gender", "start")
       ...:     .mutate(
       ...:         decade=lambda _: (ibis.date(_.start).year() / 10).cast("int32") * 10
       ...:     )
       ...:     .group_by("decade")
       ...:     .aggregate(
       ...:         n_female=lambda _: (_.bio_gender == "F").sum(),
       ...:         n_total=lambda _: _.count()
       ...:     )
       ...:     .mutate(
       ...:         percent_female=lambda _: 100 * (_.n_female / _.n_total)
       ...:     )
       ...:     .filter(lambda _: _.percent_female > 0)
       ...:     .select("decade", "percent_female")
       ...: )

    In [10]: percent_female_by_decade
    Out[10]:
        decade  percent_female
    0     1910        0.040584
    1     1920        0.883179
    2     1930        1.608363
    3     1940        1.845166
    4     1950        3.030303
    5     1960        2.718287
    6     1970        3.592073
    7     1980        4.977188
    8     1990       10.830922
    9     2000       15.865783
    10    2010       20.196641
    11    2020       27.789047

For the curious, you can see the generated SQL query using the
``ibis.show_sql`` function:

.. code-blocK:: python

    In [11]: ibis.show_sql(percent_female_by_decade)
    SELECT
      t0.decade,
      t0.percent_female
    FROM (
      SELECT
        t1.decade AS decade,
        t1.n_female AS n_female,
        t1.n_total AS n_total,
        t1.percent_female AS percent_female
      FROM (
        SELECT
          t2.decade AS decade,
          t2.n_female AS n_female,
          t2.n_total AS n_total,
          (
            t2.n_female / CAST(t2.n_total AS REAL)
          ) * 100 AS percent_female
        FROM (
          SELECT
            t3.decade AS decade,
            SUM(CAST(t3.bio_gender = 'F' AS INTEGER)) AS n_female,
            COUNT('*') AS n_total
          FROM (
            SELECT
              t4.bio_gender AS bio_gender,
              t4.start AS start,
              CAST(CAST(STRFTIME('%Y', DATE(t4.start)) AS INTEGER) / CAST(10 AS REAL) AS INTEGER) * 10 AS decade
            FROM (
              SELECT
                bio_gender,
                start
              FROM main.legislators AS t5
              JOIN main.legislator_terms AS t6
                ON t5.id = t6.legislator_id
            ) AS t4
          ) AS t3
          GROUP BY
            t3.decade
        ) AS t2
      ) AS t1
      WHERE
        t1.percent_female > 0
    ) AS t0


I wouldn't want to write all that by hand!

But then again, I'm not a SQL programmer. One benefit of Ibis is that it allows
more seamless interoperation between tools. I didn't have to handwrite the
above query, but can now share it with SQL users without requiring them to use
Python.

Completing the loop, here's a `static datasette link for the full query`_.

Wrapping Up
-----------

``ibis-datasette`` has been a fun ~1-day hack, and I hope it remains a small
and simple side project. It was definitely a good learning experience. That
said, there are a couple known warts:

- Ibis makes heavy use of ``sqlalchemy`` for both SQL generation and execution.
  This meant that I had to write both a dbapi_ and SQLAlchemy_ backend for
  ``datasette`` to get everything hooked up properly, even though it's just a
  thin wrapper around the existing ``sqlite`` backend. In the future it might
  be good to separate SQL generation from execution in ``ibis`` to simplify
  this process. This may also open up opportunities for further optimization,
  since we may be able to make use of more efficient database APIs instead of
  relying on the generic ``dbapi 2.0`` spec.

- Datasette's JSON API doesn't expose a way to provide non-string parameters
  for parametrized queries, while SQLAlchemy generates *lots* of parametrized
  queries. For now I'm hacking around this with some terrible string
  processing; since it's only for numeric values on an immutable database, the
  chance of a `Bobby Tables incident <https://xkcd.com/327/>`_ is low. It still
  feels wrong though. In the future we should be able to avoid this issue
  entirely by handling parametrization entirely in ``ibis`` (or
  ``ibis-datasette``).

I wouldn't recommend using ``ibis-datasette`` for serious work, but I've found
it a useful tool for exploring public ``datasette`` instances.

I *would* recommend using ``ibis`` and ``datasette`` for serious work though.
They're both excellent, mature libraries, bringing some user friendliness to
SQL database work.

Interested in ``ibis`` or ``ibis-datasette``? Please feel free to reach out on
`github <https://github.com/jcrist>`_ or `twitter
<https://twitter.com/jcristharif>`_.


.. _congress-legislators: https://congress-legislators.datasettes.com
.. _datasette: https://datasette.io
.. _sqlite: https://sqlite.org
.. _ibis: https://ibis-project.org
.. _dplyr: https://dplyr.tidyverse.org/
.. _linq: https://docs.microsoft.com/en-us/dotnet/csharp/programming-guide/concepts/linq/
.. _static datasette link for the full query: https://congress-legislators.datasettes.com/legislators?sql=++++SELECT%0D%0A++++++t0.decade%2C%0D%0A++++++t0.percent_female%0D%0A++++FROM+%28%0D%0A++++++SELECT%0D%0A++++++++t1.decade+AS+decade%2C%0D%0A++++++++t1.n_female+AS+n_female%2C%0D%0A++++++++t1.n_total+AS+n_total%2C%0D%0A++++++++t1.percent_female+AS+percent_female%0D%0A++++++FROM+%28%0D%0A++++++++SELECT%0D%0A++++++++++t2.decade+AS+decade%2C%0D%0A++++++++++t2.n_female+AS+n_female%2C%0D%0A++++++++++t2.n_total+AS+n_total%2C%0D%0A++++++++++%28%0D%0A++++++++++++t2.n_female+%2F+CAST%28t2.n_total+AS+REAL%29%0D%0A++++++++++%29+*+100+AS+percent_female%0D%0A++++++++FROM+%28%0D%0A++++++++++SELECT%0D%0A++++++++++++t3.decade+AS+decade%2C%0D%0A++++++++++++SUM%28CAST%28t3.bio_gender+%3D+%27F%27+AS+INTEGER%29%29+AS+n_female%2C%0D%0A++++++++++++COUNT%28%27*%27%29+AS+n_total%0D%0A++++++++++FROM+%28%0D%0A++++++++++++SELECT%0D%0A++++++++++++++t4.bio_gender+AS+bio_gender%2C%0D%0A++++++++++++++t4.start+AS+start%2C%0D%0A++++++++++++++CAST%28CAST%28STRFTIME%28%27%25Y%27%2C+DATE%28t4.start%29%29+AS+INTEGER%29+%2F+CAST%2810+AS+REAL%29+AS+INTEGER%29+*+10+AS+decade%0D%0A++++++++++++FROM+%28%0D%0A++++++++++++++SELECT%0D%0A++++++++++++++++bio_gender%2C%0D%0A++++++++++++++++start%0D%0A++++++++++++++FROM+main.legislators+AS+t5%0D%0A++++++++++++++JOIN+main.legislator_terms+AS+t6%0D%0A++++++++++++++++ON+t5.id+%3D+t6.legislator_id%0D%0A++++++++++++%29+AS+t4%0D%0A++++++++++%29+AS+t3%0D%0A++++++++++GROUP+BY%0D%0A++++++++++++t3.decade%0D%0A++++++++%29+AS+t2%0D%0A++++++%29+AS+t1%0D%0A++++++WHERE%0D%0A++++++++t1.percent_female+%3E+0%0D%0A++++%29+AS+t0%0D%0A
.. _sqlalchemy: https://www.sqlalchemy.org/
.. _dbapi: https://peps.python.org/pep-0249/
