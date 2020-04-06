A Farewell to Anaconda
######################

:date: 2020-03-20 14:30
:category: ramblings
:slug: farewell-to-anaconda
:author: Jim Crist
:summary: A recap on my last 5 years at Anaconda


In the spring of 2015 I quit my graduate program and moved to TX to work for
`Anaconda <https://www.anaconda.com/>`__ (then Continuum Analytics). Graduate
school hadn't been great for my mental health, and increasingly I was finding
the thing I liked most about my research was the software development aspects
of it. I was thrilled to be hired to help maintain the Python scientific
ecosystem full time. It was my dream job, which is why it feels so hard to say
that it's time to move on.

Today is my last day at Anaconda. I'm not leaving for any particular reason, it
just feels like it's time. I've never quit a job before, every job I've had has
had a set end time (e.g. "I'm going back to grad school" or "we can't dig holes
anymore because the ground is frozen"). It feels weird, but I'm excited for
what's next.

I'm proud of the work I helped accomplish at Anaconda. We helped create (and
maintain) open source software that is used by thousands. Here I thought I'd
recap a few of my highlights.


Dask
----

.. raw:: html

    <img title="Dask is not an acronym, our logo is just shouting its name" class="align-center" src="/images/dask-logo-horizontal.svg" style="width: 80%;" />

Most of my work for the last 5 years has been related (in one way or another)
to `Dask <https.dask.org>`__. I first started contributing while in graduate
school (~5 years ago today!). I had met Matt Rocklin the previous fall at the `Google Summer of Code
reunion <https://lwn.net/Articles/618282/>`__, where he `nerd-sniped
<https://xkcd.com/356/>`__ me into what ended up being a multi-month obsession
with term-rewriting systems (I was interested in adding one to `SymPy
<https://www.sympy.org>`__ at the time). So the following spring, when Dask
needed some rewrite-rules for it's optimizer `I was happy to help
<https://github.com/dask/dask/issues/79>`__). Thus began a career of hopelessly
understimating how long it takes to do things.

.. raw:: html

    <img title="So young, so naive." class="align-center" src="/images/first-dask-issue-comment.png" style="width: 90%;" />

The code for this still lives in ``dask.rewrite`` (docs `here
<https://docs.dask.org/en/latest/optimize.html#rewrite-rules>`__), although
it's no longer used internally. Dask has grown up a lot since then. It's now a
whole ecosystem, with
`multiple <https://anaconda.com>`__
`companies <https://coiled.io/>`__
`invested in <https://www.quansight.com/>`__
`its development <https://rapids.ai/>`__
`and maintenance <https://www.saturncloud.io/>`__.

I'm still planning on continuuing work on Dask outside of Anaconda, and am
excited to see how the project evolves over the next 5 years.


Datashader
----------

The ideas behind what would become `Datashader <https://datashader.org/>`__
(then called "abstract rendering") were first described to me at a conference
happy hour by `Peter Wang <https://twitter.com/pwang>`__. It sounded
interesting - a mix of `dask <https://dask.org/>`__, `numba
<https://numba.org>`__ and `bokeh <https://bokeh.org/>`__ - the perfect
demonstration of all the neat libraries Continuum was helping develop at the
time. I took a few weeks off from Dask development and helped write the first
version (hopefully most of my code has been rewritten at this point). It made
some pretty plots (here's an example with NYC Census data):

.. raw:: html

    <img title="NYC Census, categorized by race" class="align-center" src="/images/datashader-nyc-census.png" style="width: 90%;" />

Datashader was my first real experience developing a production library from
scratch. It worked, it was speedy, but I spent too long waffling about how the
API should be written (I think I rewrote the user-facing API 3-4 times). This
whole experience helped me learn that sometimes it's best to get things in
front of users and iterate, rather than developing "the perfect API" from the
get-go.


Python & Hadoop
---------------

During my time at Anaconda I did a few consulting projects deploying and using
Dask, mostly at large institutions. This was a useful exercise, as it revealed
many pain points when integrating with enterprise-y systems (read Hadoop). I
think it's easy for open-source devs to miss key issues if they're not also
direct users of their software. Things you might not expect to cause issues
often do.

One issue that kept cropping up was Hadoop integration. Many of our customers
had purchased large Hadoop/YARN clusters, and we had no way to run our software
on them.

.. raw:: html

    <img title="sometimes things are difficult" class="align-center" src="/images/one-does-not-simply-deploy-on-yarn.jpg" style="width: 60%;" />

While we primarily wanted to be able to run Dask on
these clusters, we also wanted a general solution. This led to `Skein
<https://jcristharif.com/skein/>`__, a (hopefully) user-friendly tool for
deploying and managing applications on Hadoop/YARN (`blogpost here
<{filename}/skein.rst>`__). While Skein was developed primarily for use in `dask-yarn
<https://yarn.dask.org>`__, it's also used by several other projects:

- `Ray <https://ray.readthedocs.io/en/latest/deploy-on-yarn.html>`__ - another distributed computing project
- `tf-yarn <https://github.com/criteo/tf-yarn>`__ - deploys tensorflow on YARN
- `jupyterhub-yarnspawner <https://jupyterhub-yarnspawner.readthedocs.io>`__ - deploys JupyterHub on YARN
- `dask-gateway <https://gateway.dask.org/>`__ - a managed deployment solution for Dask

Skein is a Python wrapper around a Java application, which meant I had to learn
Java. YARN is also mostly undocumented, which meant I had to read its source to
understand the internals (and the `madness beyond the gate
<https://steveloughran.gitbooks.io/kerberos_and_hadoop/>`__). As a result of
this I am now:

- A pretty mediocre Java developer (all of Skein looks like a Python developer
  writing Java, which is accurate).
- Fairly knowledgable about the internals of a mostly legacy system.

Future employers be warned.


JupyterHub on Hadoop
--------------------

Continuuing my rage against enterprise systems, I grew frustrated with
Cloudera's datascience workbench and developed a way to natively run
`JupyterHub <https://jupyterhub.readthedocs.io>`__ on Hadoop. It works, there's
`docs and everything
<https://jupyterhub-on-hadoop.readthedocs.io/en/latest/>`__. I even made a
walkthrough video:

.. raw:: html

    <div style="text-align:center">
      <iframe
        width="640"
        height="385"
        src="https://www.youtube.com/embed/M7T8Xnj9M6c"
        frameborder="0"
        allow="autoplay; encrypted-media;"
        allowfullscreen>
      </iframe>
    </div>

This mostly involved:

- Writing an spawner: `yarnspawner <https://jupyterhub-yarnspawner.readthedocs.io>`__
- Writing an authenticator: `kerberosauthenticator <https://jupyterhub-kerberosauthenticator.readthedocs.io>`__
- Writing a contents-manager: `hdfscm <https://jcristharif.com/hdfscm/>`__
- Documenting everything and hoping it's useful

JupyterHub is a wonderfully designed project and is a pleasure to work on. The
Jupyter community is also a model of what community-driven development can
accomplish. May Dask's community one day be equally be as open and supportive.


Dask-Gateway
------------

Dask's existing deployment solutions work well, but are inherently
decentralized. They require users to have direct access to the underlying
cluster system (e.g. Kubernetes RBAC permissions), as well as network access to
all nodes in the cluster (firewalls be damned). Likewise, users are expected to
have some knowledge of the underlying systems (e.g. K8s pod specs), which makes
onboarding trickier.

`Dask-Gateway <https://gateway.dask.org>`__ is our attempt at providing a
managed solution. It allows users to launch and use Dask clusters in a shared,
centrally managed cluster environment, without requiring users to have
knowledge of or direct access to the underlying cluster backend (e.g.
Kubernetes, Hadoop/YARN, HPC Job queues, etc…). In short, "Dask clusters as a
service".

It looks like this:

.. raw:: html

    <img title="dask-gateway's architecture" class="align-center" src="/images/dask-gateway-architecture.svg" style="width: 80%;" />

Dask-Gateway feels like a culmination of the previous work I've done:

- It's a solution for deploying *Dask*
- It works on multiple backends, including *Hadoop/YARN*
- It looks a lot like *JupyterHub* (it's basically JupyterHub, but for Dask)

This project (like any project) has been a great opportunity to learn. Before
this I had never written a serious web application, now I have *opinions* about
Python asyncio server frameworks. I also got a lot of experience working with
Enterprise Users |(TM)| whose needs and security restrictions often differ from the
usual users I encounter.

.. |(TM)| unicode:: U+2122
    :ltrim:

Dask-Gateway is currently deployed at a handful of companies, as well as
actively used as part of the `Pangeo Project <https://pangeo.io>`__. I just
finished a major rewrite of the server internals, and plan to keep developing
it in the coming months.


Retrospective
-------------

The projects discussed above don't encompass everything I've done while working
at Anaconda, but they're a sampling of my favorites. My job for the past 5
years has been to maintain and better the Python ecosystem, and in that I hope
I've been successful.

But Anaconda is more than just the software we made along the way. It's a
company full of brilliant and kind people who care about their work and the
community they're supporting. I will miss the people most.

Thanks Anaconda for a great 5 years, I truly wish you all the best.


What's Next
-----------

I'm excited to say I'm going to work at `Prefect <https://www.prefect.io/>`__.
There (among a myriad of other things), I hope to improve Prefect's integration
with Dask. I'll also be given time to continue maintenance and development of
the Dask ecosystem (bringing Prefect into the fold of companies maintaining
Dask :) ).

Before then I'm taking a few weeks off to relax. I'm returning my work laptop
to Anaconda today, and will only have access to my old college laptop (2 GiB of
RAM!) until my new job starts. Call it a forced detox from OSS development. I
have a few woodworking projects and books to keep me busy, and am looking
forward to the break.
