import api
import braille, speech, ui
import textInfos



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
