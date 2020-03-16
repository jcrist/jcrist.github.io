import os

AUTHOR = "Jim Crist-Harif"
SITENAME = "Jim Crist-Harif"
SITEURL = ""

PATH = "content"
THEME = "theme"

TIMEZONE = "America/Chicago"

DEFAULT_LANG = "en"

FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

AUTHOR_SAVE_AS = ""
AUTHORS_SAVE_AS = ""
TAGS_SAVE_AS = ""
TAG_SAVE_AS = ""
CATEGORIES_SAVE_AS = ""
CATEGORY_SAVE_AS = ""
ARCHIVES_SAVE_AS = ""

DEFAULT_PAGINATION = False
DEFAULT_DATE_FORMAT = "%B %d, %Y"

DIRECT_TEMPLATES = ["blog"]

PROFILE_IMAGE_URL = (
    "http://www.gravatar.com/avatar/85bba1ca66eb909a289448a90e88f53a?s=200"
)

MENUITEMS = [
    ("Blog", "/blog.html"),
    ("About", "/pages/about.html"),
    ("Talks", "/pages/talks.html"),
]
TEMPLATE_PAGES = {"talks.html": "pages/talks.html"}

PLUGIN_PATHS = ["./plugins", "../pelican-plugins"]
PLUGINS = ["ipynb.liquid"]
NOTEBOOK_DIR = "notebooks"
MARKUP = ["md", "rst"]

extra_dir = os.path.join(os.path.dirname(__file__), "content", "extra")
EXTRA_PATH_METADATA = {
    os.path.join("extra", f): {"path": f}
    for f in os.listdir(extra_dir)
}
STATIC_PATHS = ["images"]
STATIC_PATHS.extend(EXTRA_PATH_METADATA)

def talk(title, date, video=None, slides=None, materials=None):
    links = []
    if video:
        links.append(("Video", video))
    if slides:
        links.append(("Slides", slides))
    if materials:
        links.append(("Materials", materials))

    return {"title": title, "date": date, "links": links}


dask_talks = [
    talk(
        "Dask - Out-of-core NumPy/Pandas Through Task Scheduling",
        "SciPy 2015",
        slides="https://speakerdeck.com/jcrist/pandas-through-task-scheduling",
        video="https://youtu.be/1kkFZ4P-XHg",
    ),
    talk(
        "Parallel and Out-of-Core Python with Dask",
        "Strata 2015",
        slides="https://speakerdeck.com/jcrist/parallel-and-out-of-core-python-with-dask",
        materials="https://github.com/cpcloud/strata-nyc-2015",
    ),
    talk(
        "Dask - Parallelizing NumPy/Pandas Through Task Scheduling",
        "PyData NYC 2015",
        slides="https://speakerdeck.com/jcrist/pandas-through-task-scheduling-1",
        materials="https://github.com/jcrist/talks/tree/master/pydata_nyc_2015",
        video="https://www.youtube.com/watch?v=mHd8AI8GQhQ",
    ),
    talk(
        "Dask: Flexible Distributed Computing",
        "SciPy 2016",
        slides="http://matthewrocklin.com/slides/dask-scipy-2016.html",
        video="https://www.youtube.com/watch?v=PAGjm4BMKlk",
    ),
    talk(
        "Dask: Flexible Parallelism",
        "Harvard CS207 Guest Lecture",
        slides="https://jcristharif.com/talks/harvard_cs207_talk/slides.html",
        materials="https://github.com/jcrist/talks/tree/master/harvard_cs207_talk",
    ),
    talk(
        "Scaling Numerical Python with Dask & Numba",
        "OSBD 2016",
        slides="https://jcristharif.com/talks/osbd_workshop/slides.html",
        materials="https://github.com/jcrist/talks/tree/master/osbd_workshop",
    ),
    talk(
        "New Developments in Scaling Python Analytics",
        "Big Data Tech 2017",
        slides="https://jcristharif.com/talks/minneanalytics_2017/slides.html",
        materials="https://github.com/jcrist/talks/blob/master/minneanalytics_2017",
    ),
    talk(
        "Parallelizing Scientific Python with Dask",
        "PyData Seattle 2017",
        materials="https://github.com/jcrist/dask-tutorial-pydata-seattle-2017",
        video="https://www.youtube.com/watch?v=VAuFSo2cIhs",
    ),
    talk(
        "Make it Work, Make it Right, Make it Fast - Debugging and Profiling in Dask",
        "PyData Seattle 2017",
        slides="https://jcristharif.com/talks/profile_and_debug_dask/slides.html/",
        materials="https://github.com/jcrist/talks/tree/master/profile_and_debug_dask",
        video="https://www.youtube.com/watch?v=JoK8V2eWFPE",
    ),
    talk(
        "Parallelizing Scientific Python with Dask",
        "SciPy 2017",
        materials="https://github.com/dask/dask-tutorial/tree/scipy-2017",
        video="https://www.youtube.com/watch?v=mbfsog3e5DA",
    ),
    talk(
        "Make it Work, Make it Right, Make it Fast - Debugging and Profiling in Dask",
        "SciPy 2017",
        slides="https://jcristharif.com/talks/profile_and_debug_dask/slides.html/",
        materials="https://github.com/jcrist/talks/tree/master/profile_and_debug_dask",
        video="https://www.youtube.com/watch?v=4WUgRpl-j7Y",
    ),
    talk(
        "Parallel Data Analysis with Dask",
        "PyCon 2018",
        materials="https://github.com/TomAugspurger/dask-tutorial-pycon-2018",
        video="https://www.youtube.com/watch?v=_UWRQZ3nFm0",
    ),
    talk(
        "Parallelizing Scientific Python with Dask",
        "SciPy 2018",
        materials="https://github.com/martindurant/dask-tutorial-scipy-2018",
        video="https://www.youtube.com/watch?v=mqdglv9GnM8",
    ),
    talk(
        "Scaling PyData with Dask",
        "PyData DC 2018",
        video="https://www.youtube.com/watch?v=6ixaCnR9ur0",
        materials="https://github.com/dask/dask-tutorial",
    ),
    talk(
        "Dask Overview and Internals",
        "Dask-Summit 2019",
        slides="https://jcristharif.com/talks/dask_summit_2019/slides.html",
    ),
    talk(
        "Scaling Python with Dask",
        "AnacondaCon 2019",
        slides="https://jcristharif.com/talks/anacondacon_2019/slides.html",
        materials="https://github.com/jcrist/anacondacon-2019-tutorial",
    ),
    talk(
        "Dask-Gateway",
        "SciPy 2019 Lightning Talk",
        slides="https://jcristharif.com/talks/scipy_2019_lightning_talk/slides.html",
        video="https://youtu.be/AnYjArI2xUM?t=1771",
    ),
    talk(
        "Introducting Dask-Gateway: Dask clusters as a service",
        "PyData Austin 2019",
        video="https://www.youtube.com/watch?v=Q8Wy0RB5UKQ",
        materials="https://github.com/jcrist/talks/tree/gh-pages/pydata_austin_2019",
        slides="https://jcristharif.com/talks/pydata_austin_2019/slides.html",
    ),
    talk(
        "Dask-Gateway - Dask Clusters as a Service",
        "Dask-Summit 2020",
        slides="https://jcristharif.com/talks/dask_summit_2020/slides.html",
    ),
]

skein_talks = [
    talk(
        "Running Python on Apache YARN",
        "SciPy 2018 Lightning Talk",
        slides="https://jcristharif.com/talks/scipy_2018_lightning_talk/slides.html/",
        video="https://youtu.be/Atc3yw9OdxY?t=54m23s",
    ),
    talk(
        "Skein: a simpler way to deploy applications on Apache YARN",
        "PyData NYC 2018",
        slides="https://jcristharif.com/talks/skein_talk/slides.html",
        materials="https://github.com/jcrist/talks/tree/gh-pages/skein_talk",
    ),
    talk(
        "Skein: a simpler way to deploy applications on Apache YARN",
        "PyData DC 2018",
        slides="https://jcristharif.com/talks/skein_talk/slides.html",
        materials="https://github.com/jcrist/talks/tree/gh-pages/skein_talk",
        video="https://www.youtube.com/watch?v=WLazOYcCI_",
    ),
]

sympy_talks = [
    talk(
        "Generating Fast and Correct Code with SymPy",
        "PyMNtos 9/11/14",
        slides="https://speakerdeck.com/jcrist/generating-fast-and-correct-code-with-sympy",
        materials="https://github.com/jcrist/talks/tree/master/codegen_talk",
    ),
    talk(
        "Multibody Dynamics with SymPy and PyDy",
        "UMN Lab Seminar",
        slides="https://speakerdeck.com/jcrist/multibody-dynamics-with-sympy-and-pydy",
        materials="https://github.com/jcrist/talks/tree/master/pydy_talk",
    ),
    talk(
        "Python for the Dynamicist",
        "UMN ME8287 Guest Lecture",
        slides="https://speakerdeck.com/jcrist/python-for-the-dynamicist",
        materials="https://github.com/jcrist/talks/tree/master/dynamics_talk",
    ),
    talk(
        "Multibody Dynamics and Control with SymPy",
        "SciPy 2015",
        materials="https://github.com/pydy/pydy-tutorial-human-standing",
        video="https://www.youtube.com/watch?v=mdo2NYtA-xY",
    ),
]

TALKS = [
    ("Dask", dask_talks),
    ("Skein", skein_talks),
    ("Dynamics and SymPy", sympy_talks),
]
