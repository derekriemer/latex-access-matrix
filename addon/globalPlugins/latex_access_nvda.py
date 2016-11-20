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


from functools import wraps
import time
from logHandler import log
import NVDAObjects
import api
import braille, speech, ui# for brailling/speaking messages in NVDA
import baseObject
import config
import controlTypes
import globalPluginHandler
import globalVars
import scriptHandler
import textInfos# to get information such as caret position and the current line.
import tones
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import latex_access, latex_access.matrix_processor, latex_access.latex_access_com
sys.path.remove(sys.path[-1])

def finally_(func, final):
	"""Calls final after func, even if it fails.
	function written by  Tiler Spivy.
	"""
	def wrap(f):
		@wraps(f)
		def new(*args, **kwargs):
			try:
				func(*args, **kwargs)
			finally:
				final()
		return new
	return wrap(final)


class EditableLatex (NVDAObjects.behaviors.EditableText):
	"""
	Provides latex-access support, but makes sure this is only in edit controls.  The normal editableText.EditableText class is not used any more in this plugin because we need to take advantage of selection changes for the matrix processor.
	
	This NVDAObject overlay class is used when NVDA enters accessible Editable text, and provides the user with all the events, scripts and gestures needed to use this plugin.
	
	See the l{__gestures} dict for all the key bindings that this plugin uses.  Some may also be found in the l{GlobalPlugin} class, in the same dict.
	
	Any method beginning with event_* is an NVDA event which gets fired on other system events.
	
	Any method that begins with script_* will get executed when the required l{InputGesture} is pressed, E.G. if a key is pressed, button on the mouse is clicked, etc.
	"""

	processMaths = False
	latex_access = latex_access.latex_access_com.latex_access_com()

	matrices = []
	# For the matrices:
	matrixCount=0
	curMatrix=0


	def initOverlayClass(self):
		self.matrixBrowse = False
		self.__matrix_gestures = {}
		for c,d in [
			("upArrow", "matrixUp"),
			("downArrow", "matrixDown"),
			("leftArrow", "matrixLeft"),
			("rightArrow", "matrixRight"),
			("tab", "matrixNext"),
			("shift+tab", "matrixPrev"),
			("escape", "matrixExit"),
			("delete", "matrixDelete"),
		]:
			self.__matrix_gestures["KB:{0}".format(c)] = d

	def getScript(self, gesture):
		if not self.matrixBrowse:
			return NVDAObjects.behaviors.EditableText.getScript(self, gesture)
		log.debug(self._gestureMap)
		script = baseObject.ScriptableObject.getScript(self, gesture)
		if not script:
			script = finally_(self.script_error, self.finish)
		return script

	def finish(self):
		self.matrixBrowse = False
		self.clearGestureBindings()
		self.bindGestures(self.__gestures)
		self.bindGestures(NVDAObjects.behaviors.EditableText._EditableText__gestures)
		


	def _caretScriptPostMovedHelper(self, speakUnit, gesture, info = None):
		"""
This method ensures that LaTeX translation occurs when the system caret moves, and also makes sure that normal behaviour occurs when l{processMaths} is off.
		"""

		if scriptHandler.isScriptWaiting ():
			return

		if not info:
			try:
				info = self.makeTextInfo (textInfos.POSITION_CARET)
			except:
				return
		if config.conf["reviewCursor"]["followCaret"] and api.getNavigatorObject() is self:
			api.setReviewPosition (info)
		if speakUnit == textInfos.UNIT_LINE and EditableLatex.processMaths:
			spokenLine = GetLine ()
			brailledLine = GetLine ()
			if not spokenLine and not brailledLine:# Is it a blank line?
				spokenLine = _("blank")
				brailledLine = _("")
			else:
				spokenLine = EditableLatex.latex_access.speech (spokenLine)
				brailledLine = EditableLatex.latex_access.nemeth (brailledLine)
			speech.speakMessage (spokenLine)
			braille.handler.message (brailledLine)
		else:
			if speakUnit:
				info.expand(speakUnit)
				speech.speakTextInfo(info, unit=speakUnit, reason=controlTypes.REASON_CARET)


	def script_error(self,gesture):
		ui.message("matrix browser error: you pressed an invalid key. Browser closing.")

	def script_reportCurrentLine (self, gesture):
		"""
		This script reports the line that the current navigator object is focused on, and speaks/brailles it appropriately depending on the state of l{processMaths}.  If pressed twice quickly, the current line is spelt out.
		@param gesture: the gesture to be passed through to NVDA (in this case, a keypress).
		@type gesture: l{inputCore.InputGesture}.
		"""

		obj=api.getFocusObject()
		treeInterceptor=obj.treeInterceptor
		if hasattr(treeInterceptor,'TextInfo') and not treeInterceptor.passThrough:
			obj=treeInterceptor
		try:
			info=obj.makeTextInfo(textInfos.POSITION_CARET)
		except (NotImplementedError, RuntimeError):
			info=obj.makeTextInfo(textInfos.POSITION_FIRST)
		info.expand(textInfos.UNIT_LINE)
		if scriptHandler.getLastScriptRepeatCount()==0:
			if EditableLatex.processMaths:
				spokenLine = GetLine ()
				brailledLine = GetLine ()
				if not spokenLine and not brailledLine:# Is it a blank line?
					spokenLine = _("blank")
					brailledLine = _("")
				else:
					spokenLine = EditableLatex.latex_access.speech (spokenLine)
					brailledLine = EditableLatex.latex_access.nemeth (brailledLine)
				speech.speakMessage (spokenLine)
				braille.handler.message (brailledLine)
			else:
				speech.speakTextInfo(info,unit=textInfos.UNIT_LINE,reason=speech.REASON_CARET)
		else:
			speech.speakSpelling(info.text)
	script_reportCurrentLine.__doc__ = _("If latex-access translation is on, Translates the current line into nemeth braille and speech.  If translation is turned off, the current line is spoken as normal.  If this keystroke is pressed twice, the current line is spellt out.")

	def script_toggleDollars_nemeth (self, gesture):
		"""
		Toggles the state of whether dollar signs should be brailled in nemeth LaTeX translation.
		@param gesture: the gesture to be passed through to nvda (in this case, a keypress).
		@type gesture: l{inputCore.InputGesture}
		"""

		dollars = EditableLatex.latex_access.toggle_dollars_nemeth ()
		if dollars == True:
			ui.message (_("nemeth dollars off"))
		else:
			ui.message (_("nemeth dollars on"))
	script_toggleDollars_nemeth.__doc__ = _("Toggles the state of whether dollar signs should be brailled in nemeth LaTeX translation.")

	def script_toggleDollars_speech (self, gesture):
		"""
		Toggles the state of whether dollar signs should be spoken in speech for LaTeX translation.
		@param gesture: the gesture to be passed through to nvda (in this case, a keypress).
		@type gesture: l{inputCore.InputGesture}
		"""

		dollars = EditableLatex.latex_access.toggle_dollars_speech ()
		if dollars == True:
			ui.message (_("speech dollars off"))
		else:
			ui.message (_("speech dollars on"))
	script_toggleDollars_speech.__doc__ = _("Toggles the state of whether dollar signs should be spoken in speech for LaTeX translation.")

	def script_toggleMaths (self, Gesture):
		"""A script to toggle the latex-access translation on or off.
		@param gesture: the gesture to be past through to NVDA (in this case, a keypress).
		@type gesture: l{inputCore.InputGesture}.
		"""
		if EditableLatex.processMaths:# is translation on?
			EditableLatex.processMaths = False
			ui.message (_("Maths to be read as plain latex"))
		else:
			EditableLatex.processMaths = True# translation was off.
			ui.message (_("Maths to be processed to a more verbal form"))
	script_toggleMaths.__doc__ = _("Toggles the speaking of mathematical expressions as either straight latex or a more verbal rendering.")

	def script_inputMatrix (self, gesture):
		"""
		This script creates the matrix COM Object, and initialises a matrix based on the text that is currently selected.
		@param gesture: the gesture to be passed through to NVDA (in this case, a keypress).
		@type gesture: l{inputCore.InputGesture}
		"""
		EditableLatex.matrices.append(Matrix())
		EditableLatex.curMatrix=EditableLatex.matrixCount
		EditableLatex.matrixCount+=1
	script_inputMatrix.__doc__ = _ ("Initialises a matrix.  First highlight it and then run this script to have it as an object.")

	def script_matrixDelete(self,gesture):
		EditableLatex.matrices.remove(EditableLatex.matrices[EditableLatex.curMatrix])
		EditableLatex.matrixCount-=1
		EditableLatex.curMatrix-=1
		if self.curMatrix < 0:
			EditableLatex.curMatrix = EditableLatex.matrixCount-1
		if len(EditableLatex.matrices) == 0:
			ui.message("No more matrices exist, exiting matrix browser.")
			self.finish()
			return
		ui.message(_("Deleted matrix. Matrix  ")+str(self.curMatrix+1)+_(" Is active"))
		self.matrices[self.curMatrix].speakMatrix()
	script_matrixDelete.__doc__=_("Deletes the current matrix.")

	def script_matrixBrowser(self,gesture):
		self.matrixBrowse=True
		#alert the user of a gesture map error, rather than making the machine unusable
		self.clearGestureBindings()
		try:
			self.bindGestures(self.__matrix_gestures)
		except:
			ui.message("Error binding  browser gestures")
			self.bindGestures(self.__gestures)
			raise
		self.matrixBrowse = True
		tones.beep(100, 10)
		ui.message("Matrix browser active.")
		EditableLatex.matrices[EditableLatex.curMatrix].speakMatrix()


	def script_matrixRight (self, gesture):
		"""
		Moves the matrix one cell to the right.
		@param gesture: the gesture to be passed through to NVDA (in this case, a keypress).
		@type gesture: l{inputCore.InputGesture}
		"""
		EditableLatex.matrices[EditableLatex.curMatrix].nextColumn()
	script_matrixRight.__doc__ = _ ("moves the matrix cursor right and then speaks and brailles the cell.")

	def script_matrixLeft (self, gesture):
		"""
		Moves the matrix one cell to the left.
		@param gesture: the gesture to be passed through to NVDA (in this case, a keypress).
		@type gesture: l{inputCore.InputGesture}
		"""
		EditableLatex.matrices[EditableLatex.curMatrix].prevColumn()
	script_matrixLeft.__doc__ = _ ("Moves the matrix cursor to the left one cell, then speaks and brailles it")

	def script_matrixDown (self, gesture):
		"""
		Moves the matrix one cell down.
		@param gesture: the gesture to be passed through to NVDA (in this case, a keypress).
		@type gesture: l{inputCore.InputGesture}
		"""
		EditableLatex.matrices[EditableLatex.curMatrix].nextRow()
	script_matrixDown.__doc__ = _ ("Moves the matrix cursor down one cell, then speaks and brailles it.")

	def script_matrixUp(self, gesture):
		"""
		Moves the matrix one cell up.
		@param gesture: the gesture to be passed through to NVDA (in this case, a keypress).
		@type gesture: l{inputCore.InputGesture}
		"""
		EditableLatex.matrices[EditableLatex.curMatrix].prevRow()
	script_matrixUp.__doc__ = _ ("Moves the matrix down one cell and then speaks and brailles it.")

	def script_matrixExit(self, gesture):
		ui.message("exited matrix browser")
		self.finish()

	def script_matrixNext(self,gesture):
		if len(EditableLatex.matrices) < 2:
			ui.message("You can't switch to the next matrix. There is only one matrix at this time.")
			return
		EditableLatex.curMatrix=(EditableLatex.curMatrix+1)%EditableLatex.matrixCount #if it is mod the count, than it will reset back to 0.
		ui.message("switched to matrix "+str(EditableLatex.curMatrix+1))
		self.matrices[self.curMatrix].speakMatrix()
	script_matrixNext.__doc__=_("switches to the next matrix. Then it speaks it.")

	def script_matrixPrev(self,gesture):
		if len(EditableLatex.matrices) < 2:
			ui.message("You can't switch to the previous matrix. There is only one matrix at this time.")
			return
		if EditableLatex.curMatrix == 0:
			EditableLatex.curMatrix = EditableLatex.matrixCount-1
		else:
			EditableLatex.curMatrix-=1
		ui.message("switched to matrix "+str(EditableLatex.curMatrix+1))
		self.matrices[self.curMatrix].speakMatrix()




	# For the input gestures:
	__gestures = {
		"kb:control+M": "toggleMaths",
		"kb(desktop):NVDA+UpArrow": "reportCurrentLine",
		"kb(laptop):NVDA+l": "reportCurrentLine",
		"kb:control+D": "toggleDollars_nemeth",
		"kb:control+shift+D": "toggleDollars_speech",
		"kb:control+shift+M":"inputMatrix",
		"kb:NVDA+alt+b":"matrixBrowser",
	}

class GlobalPlugin (globalPluginHandler.GlobalPlugin):
	"""
	main class for the global plugin, in which some key bindings/scripts and NVDA events may be handled, however most of these (for this globalPlugin at least) should be in l{EditableLatex}.
	"""

	def chooseNVDAObjectOverlayClasses (self, obj, clsList):
		"""
		This is for the l{EditableLatex} object overlay class.
		"""

		windowClassName = obj.windowClassName
		if windowClassName == "Edit" or windowClassName == "Scintilla" or obj.role == controlTypes.ROLE_EDITABLETEXT:
			clsList.insert (0, EditableLatex)
	# For the key bindings:
	__gestures = {
	}

# Useful functions:
def GetLine ():
	"""Retrieves the line of text that the current navigator object is focussed on, then returns it.
	@rtype: STR
	"""

	obj = api.getFocusObject()
	treeInterceptor = obj.treeInterceptor
	if hasattr (treeInterceptor, 'TextInfo') and not treeInterceptor.passThrough:
		obj = treeInterceptor
	try:
		info = obj.makeTextInfo (textInfos.POSITION_CARET)
	except (NotImplementedError, RuntimeError):
		info = obj.makeTextInfo (textInfos.POSITION_FIRST)
	info.expand (textInfos.UNIT_LINE)
	currentLine = info.text
	return currentLine

def SayLine ():
	"""This function says the current line without any translation.  This is necessary so that we can return to NVDA's default behaviour when LaTeX translation is toggled off."""

	speech.speakMessage (GetLine())

def BrailleLine ():
	"""Brailles the current line.  This again is necessary so that we can return to NVDA's default behaviour."""

	braille.handler.message (GetLine())

def getSelectedText ():
	"""
	Retrieves, then returns the currently selected text.
	@returns: The text currently selected.
	@rtype: str
	"""

	obj = api.getFocusObject ()
	treeInterceptor = obj.treeInterceptor
	if hasattr (treeInterceptor, 'TextInfo') and not treeInterceptor.passThrough:
		obj = treeInterceptor
	try:
		info = obj.makeTextInfo(textInfos.POSITION_SELECTION)
	except (RuntimeError, NotImplementedError):
		info = None
	if not info or info.isCollapsed:
		return None
	else:
		return info.text
