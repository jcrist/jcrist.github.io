TIL: How to mark a package as broken on PyPI & Conda-Forge
##########################################################

:date: 2023-02-10 16:36
:slug: til-broken-pypi-conda-forge-packages
:author: Jim Crist-Harif
:summary: What to do when you release a broken build to PyPI and Conda-Forge

It finally happened: I released a critically broken package (`msgspec 0.13.0
<https://github.com/jcrist/msgspec>`__) to PyPI and Conda-Forge. Mistakes
happen, and a patch release was pushed up within 24 hours, but I still wanted
to prevent users from accidentally installing the broken package.

In these situations, neither `PyPI <https://pypi.org/>`__ nor `conda-forge
<https://conda-forge.org/>`__ recommend (or support) deleting the release.
Rather they have their own mechanisms for marking a release as "broken" so
users will only end up with that version if they've pinned specifically to that
version.

PyPI
----

For PyPI you'll want to `"yank" <https://pypi.org/help/#yanked>`__ the release.
This may be done through the admin page on PyPI for your project. Click the "Option"
dropdown next to the faulty release, then click "Yank".

.. raw:: html

    <img title="screenshot of PyPI.org" class="align-center" src="/images/pypi-yank.png" style="width: 60%;" />

Yanking a release removes that release from PyPI's UI. ``pip`` and other tools
will also avoid installing yanked releases *unless* the user has explicitly
pinned to that version.

.. code-block:: text

    # won't get the yanked release
    $ pip install msgspec

    # will get the yanked release, since they've pinned to that version
    $ pip install msgspec=0.13.0

Conda-Forge
-----------

For Conda-Forge the process is a bit more involved, but has the same end
effect. Following the instructions from the `official conda-forge docs
<https://conda-forge.org/docs/maintainer/updating_pkgs.html#removing-broken-packages>`__:

- I forked the `conda-forge/admin-requests
  <https://github.com/conda-forge/admin-requests>`__ repository to my personal
  GitHub account.

- Added a new ``msgspec.txt`` file to the ``broken/`` directory. Each line of
  that file should be a filename for a broken release artifact. In my case I
  wanted to mark all 24 different builds of ``msgspec 0.13.0`` as broken. These
  filenames were easiest to find with a short script using the `anaconda.org
  API <https://api.anaconda.org/docs>`__:

.. code-block:: python

    import requests
    
    package = "msgspec"
    version = "0.13.0"

    resp = requests.get(f"https://api.anaconda.org/release/conda-forge/{package}/{version}")
    for dist in resp.json()["distributions"]:
        print(dist["basename"])


.. code-block:: txt

    linux-64/msgspec-0.13.0-py310h1fa729e_0.conda
    linux-64/msgspec-0.13.0-py311h2582759_0.conda
    linux-64/msgspec-0.13.0-py38h1de0b5d_0.conda
    linux-64/msgspec-0.13.0-py39h72bdee0_0.conda
    linux-aarch64/msgspec-0.13.0-py310hb89b984_0.conda
    linux-aarch64/msgspec-0.13.0-py311h1d6c08a_0.conda
    linux-aarch64/msgspec-0.13.0-py38hda48048_0.conda
    linux-aarch64/msgspec-0.13.0-py39h24fc6b6_0.conda
    linux-ppc64le/msgspec-0.13.0-py310h82c586f_0.conda
    linux-ppc64le/msgspec-0.13.0-py311h57b9580_0.conda
    linux-ppc64le/msgspec-0.13.0-py38h0c7bae7_0.conda
    linux-ppc64le/msgspec-0.13.0-py39h38a9e30_0.conda
    osx-64/msgspec-0.13.0-py310h90acd4f_0.conda
    osx-64/msgspec-0.13.0-py311h5547dcb_0.conda
    osx-64/msgspec-0.13.0-py38hef030d1_0.conda
    osx-64/msgspec-0.13.0-py39ha30fb19_0.conda
    osx-arm64/msgspec-0.13.0-py310h8e9501a_0.conda
    osx-arm64/msgspec-0.13.0-py311he2be06e_0.conda
    osx-arm64/msgspec-0.13.0-py38hb991d35_0.conda
    osx-arm64/msgspec-0.13.0-py39h02fc5c5_0.conda
    win-64/msgspec-0.13.0-py310h8d17308_0.conda
    win-64/msgspec-0.13.0-py311ha68e1ae_0.conda
    win-64/msgspec-0.13.0-py38h91455d4_0.conda
    win-64/msgspec-0.13.0-py39ha55989b_0.conda

- Once that was done, I `pushed up a PR with the changes
  <https://github.com/conda-forge/admin-requests/pull/675>`__. An admin merged
  this pretty quickly (thanks!), and the conda-forge bots marked the respective
  builds as broken.
