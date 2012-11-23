# This file is part of ReText
# Copyright: Dmitry Shachnev 2012
# License: GNU GPL v2 or higher

import markups
from subprocess import Popen, PIPE

def detect_qt_package():
	"""Determines which version of qt (PyQt4 or PySide) to use"""
	try:
		import PyQt4
		return "PyQt4"
	except ImportError, PyQt4_import_error:
		pass
	try:
		import PySide
		return "PySide"
	except ImportError, PySide_import_error:
		pass
	raise ImportError("Error importing PyQt4 (%s) and PySide (%s). One of these libraries is required to run ReText" % (PyQt4_import_error, PySide_import_error))

qt_package_name = detect_qt_package()
if qt_package_name == "PyQt4":
	from PyQt4.QtCore import *
	from PyQt4.QtGui import *
elif qt_package_name == "PySide":
	from PySide.QtCore import *
	from PySide.QtGui import *

app_name = "ReText"
app_version = "4.0 (Git)"

settings = QSettings('ReText project', 'ReText')

if not str(settings.fileName()).endswith('.conf'):
	# We are on Windows probably
	settings = QSettings(QSettings.IniFormat, QSettings.UserScope, 
		'ReText project', 'ReText')

try:
	import enchant
	enchant.Dict()
except:
	enchant_available = False
else:
	enchant_available = True

icon_path = "icons/"

DOCTYPE_NONE = ''
DOCTYPE_MARKDOWN = markups.MarkdownMarkup.name
DOCTYPE_REST = markups.ReStructuredTextMarkup.name
DOCTYPE_HTML = 'html'

try:
	if qt_package_name == "PyQt4":
		from PyQt4.QtWebKit import QWebView, QWebPage
	elif qt_package_name == "PySide":
		from PySide.QtWebKit import QWebView, QWebPage
except:
	webkit_available = False
else:
	webkit_available = True

def readFromSettings(key, keytype, settings=settings, default=None):
	if not settings.contains(key):
		return default
	try:
		return settings.value(key, type=keytype)
	except TypeError as error:
		if str(error).startswith('unable to convert'):
			# New PyQt version, but type mismatch
			print('Warning: '+str(error))
			# Return an instance of keytype
			return default if (default is not None) else keytype()
		# For old PyQt versions
		if keytype == str:
			return settings.value(key).toString()
		elif keytype == int:
			result, ok = settings.value(key).toInt()
			if not ok:
				print('Warning: cannot covert settings value to int!')
			return result
		elif keytype == bool:
			return settings.value(key).toBool()
		elif keytype == QByteArray:
			return settings.value(key).toByteArray()

def readListFromSettings(key, settings=settings):
	if not settings.contains(key):
		return []
	value = settings.value(key)
	try:
		return value.toStringList()
	except:
		# For Python 3
		if isinstance(value, str):
			return [value]
		else:
			return value

def writeListToSettings(key, value, settings=settings):
	if len(value) > 1:
		settings.setValue(key, value)
	elif len(value) == 1:
		settings.setValue(key, value[0])
	else:
		settings.remove(key)

def convertToUnicode(string):
	try:
		return unicode(string)
	except:
		# For Python 3
		return string

monofont = QFont()
monofont.setFamily(readFromSettings('editorFont', str, default='monospace'))
if settings.contains('editorFontSize'):
	monofont.setPointSize(readFromSettings('editorFontSize', int))
