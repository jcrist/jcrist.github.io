AUTHOR = 'Jim Crist-Harif'
SITENAME = 'Jim Crist-Harif'
SITEURL = ''

PATH = 'content'
THEME = 'theme'

TIMEZONE = 'America/Chicago'

DEFAULT_LANG = 'en'

FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

AUTHOR_SAVE_AS = ''
AUTHORS_SAVE_AS = ''
TAGS_SAVE_AS = ''
TAG_SAVE_AS = ''
CATEGORIES_SAVE_AS = ''
CATEGORY_SAVE_AS = ''
ARCHIVES_SAVE_AS = ''

DEFAULT_PAGINATION = False
DEFAULT_DATE_FORMAT = '%B %d, %Y'

DIRECT_TEMPLATES = ['blog']

PROFILE_IMAGE_URL = 'http://www.gravatar.com/avatar/85bba1ca66eb909a289448a90e88f53a?s=200'

MENUITEMS = [('Blog', '/blog.html'), 
             ('About', '/pages/about.html'),
             ('Talks', '/pages/talks.html')]

PLUGIN_PATHS = ['./plugins', '../pelican-plugins']
PLUGINS = ['ipynb.liquid']
NOTEBOOK_DIR = 'notebooks'
MARKUP = ['md', 'rst']

STATIC_PATHS = ['images', 'extra/CNAME']
EXTRA_PATH_METADATA = {'extra/CNAME': {'path': 'CNAME'},}
