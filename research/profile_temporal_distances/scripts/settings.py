RESULTS_DIRECTORY = "../results/"
HELSINKI_DATA_BASEDIR = "../data/helsinki/2016-09-28/"
HELSINKI_NODES_FNAME = HELSINKI_DATA_BASEDIR + "main.day.nodes.csv"

DEFAULT_TILES = "CartoDB positron"
DARK_TILES = "CartoDB dark_matter"

ROUTING_START_TIME_DEP = 1475463600  # 06:00 AM

ANALYSIS_START_TIME_DEP = ROUTING_START_TIME_DEP  # 07:00
ANALYSIS_END_TIME_DEP = ROUTING_START_TIME_DEP + 2 * 3600

ROUTING_END_TIME_DEP = ROUTING_START_TIME_DEP + 8 * 3600

from jinja2 import defaults
defaults.LSTRIP_BLOCKS = True
defaults.KEEP_TRAILING_NEWLINE = False
defaults.TRIM_BLOCKS = True
