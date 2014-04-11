#!/bin/sh
# If you are running in a virtualenv, activate it before invoking this script.
# Also update the script if you add any tests for content plugins.
nosetests test_generic_string_matcher.py test_bmc.py test_cell_reports.py test_copernicus.py test_elife.py test_hindawi.py test_nature.py test_oup.py
