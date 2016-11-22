#    latex_access.py
#    A part of the latex-access project at http://latex-access.sourceforge.net/
#    Author: Nathaniel Schmidt <nathanieljsch@westnet.com.au> Modifyed by Derek Riemer
#    Copyright (C) 2011-2016 Nathaniel Schmidt, Derek Riemer, and Latex-access Contributors
#
#    This program is free software; you can redistribute it
#    and/or modify it under the terms of the GNU General Public License as published
#    by the Free Software Foundation;
#    either version 2 of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#    See the GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along with this program; if not, visit <http://www.gnu.org/licenses/old-licenses/gpl-2.0.html>

"""
A global plugin for NVDA to provide optional translations of LaTeX math into Nemeth and UEB Braille and speech that is easier to understand, by way of latex-access.  See readme.txt for more information.

Features:
	* Translating lines of LaTeX into nemeth braille and speech - status: completed.
	* matrix browser for reading larger matrices - status: under development.
	* The preprocessor (support for custom defined LaTeX commands) - status: not completed.
	* Access to tables - status: not completed.
	* access to motion for moving quickly through mathematical terms - status: N/A.
"""

import globalPluginHandler
import scriptHandler
import os, sys
from editableText import EditableText
from editableLatex import EditableLatex

class GlobalPlugin (globalPluginHandler.GlobalPlugin):
	"""
	main class for the global plugin, in which some key bindings/scripts and NVDA events may be handled, however most of these (for this globalPlugin at least) should be in l{EditableLatex}.
	"""

	def chooseNVDAObjectOverlayClasses (self, obj, clsList):
		"""
		This is for the l{EditableLatex} object overlay class.
		"""
		for i in clsList:
			if issubclass(i, EditableText):
				clsList.insert (0, EditableLatex)
				break
