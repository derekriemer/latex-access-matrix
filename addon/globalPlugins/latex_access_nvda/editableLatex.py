import time
import os
import sys
from globalFunctions import *
import NVDAObjects
import config
import api
import matrixBrowser
import braille, speech, ui
import controlTypes
import textInfos
import scriptHandler
import tones
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import latex_access, latex_access.latex_access_com
sys.path.remove(sys.path[-1])

class EditableLatex(NVDAObjects.behaviors.EditableText):
	"""
	Provides latex-access support, but makes sure this is only in edit controls.  The normal editableText.EditableText class is not used any more in this plugin because we need to take advantage of selection changes for the matrix processor.
	
	This NVDAObject overlay class is used when NVDA enters accessible Editable text, and provides the user with all the events, scripts and gestures needed to use this plugin.
	
	See the l{__gestures} dict for all the key bindings that this plugin uses.  Some may also be found in the l{GlobalPlugin} class, in the same dict.
	
	Any method beginning with event_* is an NVDA event which gets fired on other system events.
	
	Any method that begins with script_* will get executed when the required l{InputGesture} is pressed, E.G. if a key is pressed, button on the mouse is clicked, etc.
	"""

	processMaths = False
	latex_access = latex_access.latex_access_com.latex_access_com()
	_firstMatrix=None#points at an NVDAObject
	_curMatrix=None#points at the NVDAObject representing the currently selected matrix
	_lastMatrix=None#points at an NVDAObject

	def _get_firstMatrix(self):
		return EditableLatex._firstMatrix

	def _set_firstMatrix(self, value):
		EditableLatex._firstMatrix = value

	def _get_lastMatrix(self):
		return EditableLatex._lastMatrix

	def _set_lastMatrix(self, value):
		EditableLatex._lastMatrix = value

	def _get_curMatrix(self):
		return EditableLatex._curMatrix

	def _set_curMatrix(self, value):
		EditableLatex._curMatrix = value

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
		if self.curMatrix is None: #First matrix to exist.
			cur = matrixBrowser.MatrixBrowserNVDAObject(latex = getSelectedText(), chooseBestAPI=False)
			EditableLatex.firstMatrix = EditableLatex.lastMatrix = EditableLatex.curMatrix = cur 
			print EditableLatex.firstMatrix
		else:
			EditableLatex.lastMatrix = EditableLatex.lastMatrix.create(getSelectedText())
	script_inputMatrix.__doc__ = _ ("Initialises a matrix.  First highlight it and then run this script to have it as an object.")
	
	def script_matrixBrowser(self,gesture):
		if EditableLatex.firstMatrix == None:
			tones.beep(800, 300)
			time.sleep(.350)
			tones.beep(600, 400)
			time.sleep(.450)
			tones.beep(400, 500)
			time.sleep(.550)
			ui.message("No matrices exist, save one first.")
			return
		tones.beep(400, 100)
		ui.message("Matrix browser active.")
		self.curMatrix.setFocus()

	# For the input gestures:
	__gestures = {
		"kb:control+nvda+shift+M": "toggleMaths",
		"kb(desktop):NVDA+UpArrow": "reportCurrentLine",
		"kb(laptop):NVDA+l": "reportCurrentLine",
		"kb:control+nvda+shift+D": "toggleDollars_nemeth",
		"kb:alt+shift+nvda+D": "toggleDollars_speech",
		"kb:alt+nvda+M":"inputMatrix",
		"kb:NVDA+alt+b":"matrixBrowser",
	}

