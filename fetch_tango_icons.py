#!/usr/bin/env python

import logging
import os
import re
import sys
import tarfile
import urllib

os.chdir(os.path.abspath(os.path.dirname(__file__)))
# fetches tango icons

TANGO_VERSION = '0.8.90'
TANGO_FILENAME = 'tango-icon-theme-%s.tar.gz' % TANGO_VERSION
ICONS_DIR = "icons"
DOWNLOAD_DIR = os.path.join(ICONS_DIR, "download")
ICON_PATTERNS = [re.compile(regex) for regex in (r"icon='([^']*)'", r"fromTheme[(]'([^']*)'[)]", r"icon_path+'([']*)[.][a-z][a-z][a-z]']")]
REPLACE_MAP = {
	'application-exit': 'system-log-out',
	'help-about': 'retext',
	'help-contents': 'help-browser',
	'document-preview': 'x-office-document',
}

icons = set()
for line in open(os.path.join("ReText", "window.py")):
	for icon_pattern in ICON_PATTERNS:
		icons.update(icon_pattern.findall(line))

if not os.path.exists(DOWNLOAD_DIR):
	os.mkdir(DOWNLOAD_DIR)
tango_path = os.path.join(DOWNLOAD_DIR, TANGO_FILENAME)
if os.path.exists(tango_path):
	# try access it
	try:
		archive = tarfile.open(tango_path, "r:gz")
		names = archive.getnames()
	except IOError:
		logging.warning("Existing file %s seems corrupt/incomplete: removing to redownload", tango_path)
		os.remove(tango_path)

if not os.path.exists(tango_path):
	urllib.urlretrieve('http://tango.freedesktop.org/releases/%s' % (TANGO_FILENAME,), tango_path)
archive = tarfile.open(tango_path, "r:gz")
svg_prefix = "tango-icon-theme-%s/scalable/" % (TANGO_VERSION,)
svg_items_map = dict((name[name.rfind("/")+1:-4], name) for name in archive.getnames() if name.startswith(svg_prefix) and name.endswith(".svg"))

for icon in sorted(icons):
	source_icon = REPLACE_MAP.get(icon, icon)
	if source_icon in svg_items_map:
		archive_file = archive.extractfile(svg_items_map[source_icon])
		try:
			file_contents = archive_file.read()
		finally:
			archive_file.close()
		with open(os.path.join(ICONS_DIR, icon+".svg"), "wb") as icon_file:
			icon_file.write(file_contents)
	elif os.path.exists(os.path.join(ICONS_DIR, source_icon+".svg")):
		with open(os.path.join(ICONS_DIR, source_icon+".svg"), "rb") as archive_file:
			file_contents = archive_file.read()
		with open(os.path.join(ICONS_DIR, icon+".svg"), "wb") as icon_file:
			icon_file.write(file_contents)
	elif os.path.exists(os.path.join(ICONS_DIR, icon+".svg")):
		logging.info("Not writing over existing icon %s", icon)
	else:
		logging.warning("Can't find icon %s", icon)

