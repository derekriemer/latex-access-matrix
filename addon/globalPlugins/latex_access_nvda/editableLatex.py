import time
import os
import sys
import re
from globalFunctions import *
import NVDAObjects
import config
import api
import matrixBrowser
import braille, speech, ui
from braille import NVDAObjectHasUsefulText, ReviewTextInfoRegion, CursorManagerRegion, TextInfoRegion
import louis
import controlTypes
import textInfos
import scriptHandler
import tones
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import latex_access, latex_access.speech, latex_access.nemeth
sys.path.remove(sys.path[-1])

TEXT_SEPARATOR = " "

MATH_MATCHER = re.compile(
	r"<(/?(?:sup|sub))>|"
		r"[^<]+"
)


class LatexBrailleRegion(TextInfoRegion):
	"""Braille and routing support for regions when latex-access is on."""
	def __init__(self, obj):
		super(LatexBrailleRegion, self).__init__(obj)
		self.realRawText=""
		self.realRawToBraillePos = []
		

	def update(self):
		#Unfortunately, we cannot use the base implementation, because we need to do custom stuff.
		#Therefore, this has a lot copied verbatim 
		formatConfig = config.conf["documentFormatting"]
		unit = self._getReadingUnit()
		self.rawText = ""
		self.rawTextTypeforms = []
		self.cursorPos = None
		# The output includes text representing fields which isn't part of the real content in the control.
		# Therefore, maintain a map of positions in the output to positions in the content.
		self._rawToContentPos = []
		self._currentContentPos = 0
		self.selectionStart = self.selectionEnd = None
		self._isFormatFieldAtStart = True
		self._skipFieldsNotAtStartOfNode = False
		self._endsWithField = False

		# Selection has priority over cursor.
		# HACK: Some TextInfos only support UNIT_LINE properly if they are based on POSITION_CARET,
		# and copying the TextInfo breaks this ability.
		# So use the original TextInfo for line and a copy for cursor/selection.
		self._readingInfo = readingInfo = self._getSelection()
		sel = readingInfo.copy()
		if not sel.isCollapsed:
			# There is a selection.
			if self.obj.isTextSelectionAnchoredAtStart:
				# The end of the range is exclusive, so make it inclusive first.
				readingInfo.move(textInfos.UNIT_CHARACTER, -1, "end")
			# Collapse the selection to the unanchored end.
			readingInfo.collapse(end=self.obj.isTextSelectionAnchoredAtStart)
			# Get the reading unit at the selection.
			readingInfo.expand(unit)
			# Restrict the selection to the reading unit.
			if sel.compareEndPoints(readingInfo, "startToStart") < 0:
				sel.setEndPoint(readingInfo, "startToStart")
			if sel.compareEndPoints(readingInfo, "endToEnd") > 0:
				sel.setEndPoint(readingInfo, "endToEnd")
		else:
			# There is a cursor.
			# Get the reading unit at the cursor.
			readingInfo.expand(unit)

		# Not all text APIs support offsets, so we can't always get the offset of the selection relative to the start of the reading unit.
		# Therefore, grab the reading unit in three parts.
		# First, the chunk from the start of the reading unit to the start of the selection.
		chunk = readingInfo.copy()
		chunk.collapse()
		chunk.setEndPoint(sel, "endToStart")
		self._addTextWithFields(chunk, formatConfig)
		# If the user is entering braille, place any untranslated braille before the selection.
		# Import late to avoid circular import.
		import brailleInput
		text = brailleInput.handler.untranslatedBraille
		if text:
			rawInputIndStart = len(self.rawText)
			# _addFieldText adds text to self.rawText and updates other state accordingly.
			self._addFieldText(INPUT_START_IND + text + INPUT_END_IND, None, separate=False)
			rawInputIndEnd = len(self.rawText)
		else:
			rawInputIndStart = None
		# Now, the selection itself.
		self._addTextWithFields(sel, formatConfig, isSelection=True)
		# Finally, get the chunk from the end of the selection to the end of the reading unit.
		chunk.setEndPoint(readingInfo, "endToEnd")
		chunk.setEndPoint(sel, "startToEnd")
		self._addTextWithFields(chunk, formatConfig)

		# Strip line ending characters.
		self.rawText = self.rawText.rstrip("\r\n\0\v\f")
		rawTextLen = len(self.rawText)
		if rawTextLen < len(self._rawToContentPos):
			# The stripped text is shorter than the original.
			self._currentContentPos = self._rawToContentPos[rawTextLen]
			del self.rawTextTypeforms[rawTextLen:]
			# Trimming _rawToContentPos doesn't matter,
			# because we'll only ever ask for indexes valid in rawText.
			#del self._rawToContentPos[rawTextLen:]
		if rawTextLen == 0 or not self._endsWithField:
			# There is no text left after stripping line ending characters,
			# or the last item added can be navigated with a cursor.
			# Add a space in case the cursor is at the end of the reading unit.
			self.rawText += TEXT_SEPARATOR
			rawTextLen += 1
			self.rawTextTypeforms.append(louis.plain_text)
			self._rawToContentPos.append(self._currentContentPos)
		if self.cursorPos is not None and self.cursorPos >= rawTextLen:
			self.cursorPos = rawTextLen - 1
		# The selection end doesn't have to be checked, Region.update() makes sure brailleSelectionEnd is valid.
		# If this is not the start of the object, hide all previous regions.
		start = readingInfo.obj.makeTextInfo(textInfos.POSITION_FIRST)
		self.hidePreviousRegions = (start.compareEndPoints(readingInfo, "startToStart") < 0)
		# Don't touch focusToHardLeft if it is already true
		# For example, it can be set to True in getFocusContextRegions when this region represents the first new focus ancestor
		# Alternatively, BrailleHandler._doNewObject can set this to True when this region represents the focus object and the focus ancestry didn't change
		if not self.focusToHardLeft:
			# If this is a multiline control, position it at the absolute left of the display when focused.
			self.focusToHardLeft = self._isMultiline()
		#Get braille for the latex.
		#Unfortunately, latex-access returns ascii braille, not dots. Fake this now.
		if self.obj.processMaths:
			print "yack"
			self.realRawText = self.rawText
			self.realRawToBraillePos = self.rawToBraillePos
			self.rawText = self.obj.nemeth.translate(self.rawText)
			self.rawToBraillePos = self.obj.nemeth.trans2src
		braille.Region.update(self)

	

class EditableLatex(NVDAObjects.behaviors.EditableText):
	"""
	Provides latex-access support, but makes sure this is only in edit controls.  The normal editableText.EditableText class is not used any more in this plugin because we need to take advantage of selection changes for the matrix processor.
	
	This NVDAObject overlay class is used when NVDA enters accessible Editable text, and provides the user with all the events, scripts and gestures needed to use this plugin.
	
	See the l{__gestures} dict for all the key bindings that this plugin uses.  Some may also be found in the l{GlobalPlugin} class, in the same dict.
	
	Any method beginning with event_* is an NVDA event which gets fired on other system events.
	
	Any method that begins with script_* will get executed when the required l{InputGesture} is pressed, E.G. if a key is pressed, button on the mouse is clicked, etc.
	"""

	processMaths = False
	speech = latex_access.speech.speech()
	nemeth = latex_access.nemeth.nemeth()
	_firstMatrix=None#points at an NVDAObject
	_curMatrix=None#points at the NVDAObject representing the currently selected matrix
	_lastMatrix=None#points at an NVDAObject
	_currentFocus=None
	
	

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

	def _get_currentFocus(self):
		"""Gets the current focus. This is intended to help the parent focus the proper thing after the matrix browser closes.
		"""
		return EditableLatex._currentFocus

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
			#We don't need to get braille. It's handled by the region.
			if not spokenLine:# Is it a blank line?
				spokenLine = _("blank")
			else:
				self.speakMathLine(spokenLine)
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
		#obj is an alias for self. to ease maintenence in Inherited code.
		obj = self
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
				if not spokenLine:# Is it a blank line?
					spokenLine = _("blank")
				else:
					self.speakMathLine(spokenLine)
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
		dollars = self.nemeth.remove_dollars=not self.nemeth.remove_dollars
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
		dollars = self.speech.remove_dollars=not self.speech.remove_dollars
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
			self.firstMatrix = self.lastMatrix = self.curMatrix = cur
			print self.firstMatrix
		else:
			self.lastMatrix = self.lastMatrix.create(getSelectedText())
	script_inputMatrix.__doc__ = _ ("Initialises a matrix.  First highlight it and then run this script to have it as an object.")
	
	def script_matrixBrowser(self,gesture):
		if self.firstMatrix == None:
			tones.beep(800, 300)
			time.sleep(.350)
			tones.beep(600, 400)
			time.sleep(.450)
			tones.beep(400, 500)
			time.sleep(.550)
			ui.message("No matrices exist, save one first.")
			return
		tones.beep(400, 200)
		ui.message("Matrix browser active.")
		EditableLatex._currentFocus = self
		#We will set the parent of all the matrices to this object's, because otherwise, NVDA reads the title of that window damn it.
		matrix = self.firstMatrix
		while matrix:
			matrix.parent  = self
			matrix = matrix.next
		self.curMatrix.setFocus()

	def speakMathLine(self, spokenLine):
		spokenLine = EditableLatex.speech.translate (spokenLine)
		out = []
		sups = 0 #How many superscripts we are in.
		subs = 0 #How many subscripts we are in.
		for expr in MATH_MATCHER.finditer(spokenLine):
			if expr.group(1) == "sup":
				sups+=1
				#If there are any subscripts, do not pitch it, as we pitched the subscript.
				#If there are any superscripts nessted, don't pitch it, because voice control isn't good enough for this in NVDA.
				if sups == 1 and not subs:
					out.append(speech.PitchCommand(1.25))
				out.append("soop")
				out.append(speech.BreakCommand(200))
			elif expr.group(1) == "/sup":
				sups -= 1
				out.append("End soop")
				if not sups and not subs:
					#we know we are in nothing. turn the pitch change off.
					out.append(speech.PitchCommand(1))
				out.append(speech.BreakCommand(200))
			elif expr.group(1) == "sub":
				subs += 1
				if subs == 1 and sups == 0:
					out.append(speech.PitchCommand(.25))
				out.append("sub")
				out.append(speech.BreakCommand(200))
			elif expr.group(1) == "/sub":
				subs -= 1
				out.append("End sub")
				if not subs and not sups:
					out.append(speech.PitchCommand(1))
				out.append(speech.BreakCommand(200))
			else:
				#all other math. Send er.
				out.append(expr.group(0))
		speech.speak(out)


	def getBrailleRegions(self, review=False):
		"""Return modified braille regions for la tex.
		"""
		#Until I get braille working better, it's disabled.
		if False and self.processMaths:
			region2 = LatexBrailleRegion(self)
		else:
			# Late import to avoid circular import.
			from treeInterceptorHandler import TreeInterceptor, DocumentTreeInterceptor
			from cursorManager import CursorManager
			from NVDAObjects import NVDAObject
			if isinstance(self, CursorManager):
				region2 = (ReviewTextInfoRegion if review else CursorManagerRegion)(self)
			elif isinstance(self, DocumentTreeInterceptor) or (isinstance(self,NVDAObject) and NVDAObjectHasUsefulText(self)):
				region2 = (ReviewTextInfoRegion if review else TextInfoRegion)(self)
			else:
				region2 = None
		region =braille.NVDAObjectRegion(self)
		return (region, region2)

	# For the input gestures:
	__gestures = {
		"kb:control+nvda+shift+M": "toggleMaths",
		"kb(desktop):NVDA+UpArrow": "reportCurrentLine",
		"kb(laptop):NVDA+l": "reportCurrentLine",
		"kb:alt+nvda+n": "toggleDollars_nemeth",
		"kb:alt+nvda+d": "toggleDollars_speech",
		"kb:alt+nvda+M":"inputMatrix",
		"kb:NVDA+alt+b":"matrixBrowser",
	}

