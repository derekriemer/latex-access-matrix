import sys,os
from mathPres import MathInteractionNVDAObject
import ui
import speech
import eventHandler
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
import latex_access.matrix_processor
sys.path.remove(sys.path[-1])

class MatrixBrowserNVDAObject(MathInteractionNVDAObject):
	"""
	An NVDA object allowing for navigation through matrices. 
	Pressing tab and shift+tab focus the next and previous matrix. 
	Pressing arrow keys allow for movement around this matrix.
	"""
	windowClassName=u"NVDAMathObject"

	def __init__(self, provider=None, latex=None, cur=None, matrixNumber=1):
		super(MatrixBrowserNVDAObject, self).__init__(provider=provider)
		self.matrix=latex_access.matrix_processor.matrix()
		self.matrix.tex_init(latex )
		# The msg variable is here to say how many rows and columns have been initialised.
		msg = _("Initialised")
		msg = msg + str (self.matrix.rows)
		msg = msg + _(" by ")
		msg = msg + str(self.matrix.columns)
		msg = msg +_( " matrix")
		ui.message (msg)
		self.matrixNumber = matrixNumber
		self.row=1
		self.column=1
		self.previous = cur
		self.next = None

	def create(self, latex):
		if self.next is not None:
			raise ValueError("You must only create a matrix at the end of the set")
		self.next = MatrixBrowserNVDAObject(latex = latex, cur=self, matrixNumber = self.matrixNumber+1, chooseBestAPI=False)
		return self.next

	def speakMatrix(self):
		matrix=[
			"Matrix %d" % self.matrixNumber,
			"Begin matrix",
			speech.BreakCommand(400)]
		for i in range(1, self.matrix.rows+1) :
			matrix+=self.speakRow(i)
			matrix.append(speech.BreakCommand(300))
		speech.speak(matrix+["end matrix"])

	def speakRow(self, row):
		temp = ["row "+str(row)+": ",
			speech.BreakCommand(300)]
		#This unfortunately is very buggie on espeak, so I'm removing it for now.
		#temp.append(speech.PitchCommand(1.25))
		for i in xrange(1,self.matrix.columns+1):
			temp+=[str(self.matrix.get_cell(row,i)), speech.BreakCommand(180)]
		#temp.append(speech.PitchCommand(0.25))
		return temp

	def isOnlyMatrix(self):
		return not (self.next or  self.previous)

	def reportFocus(self, verbose=False):
		if verbose:
			self.speakMatrix()
		else:
			msg = "Matrix {} at  {} {} value {}".format(
									self.matrixNumber, self.row, self.column,
									self.matrix.get_cell(self.row, self.column))
			ui.message(msg)
			

	def script_nextRow(self, gesture):
		""" Increases the row count by 1 if possible, speaking the new row, or speaks that the edge was reached. """
		if self.row == self.matrix.rows:
			ui.message("End of column.")
		else:
			self.row+=1
			ui.message (self.matrix.get_cell(self.row, self.column))

	def script_previousRow(self, gesture):
		"""Decreases the row count by 1 if possible, speaking the new row, or speaks that the edge was reached. """
		if self.row == 1:
			ui.message("beginning of column.")
		else:
			self.row-=1
			ui.message (self.matrix.get_cell(self.row, self.column))

	def script_nextColumn(self, gesture):
		""" Increases the column count by 1 if possible, speaking the new column, or speaks that the edge was reached. """
		if self.column == self.matrix.columns:
			ui.message("End of row.")
		else:
			self.column+=1
			ui.message (self.matrix.get_cell(self.row, self.column))

	def script_previousColumn(self, gesture):
		""" Increases the column count by 1 if possible, speaking the new column, or speaks that the edge was reached. """
		if self.column == 1:
			ui.message("Beginning of row.")
		else:
			self.column-=1
			ui.message (self.matrix.get_cell(self.row, self.column))

	def script_deleteMatrix(self, gesture):
		if self.isOnlyMatrix():
			#last matrix in browser. Clean up.
			self.parent.curMatrix = self.parent.firstMatrix = self.parent.lastMatrix = None
			eventHandler.executeEvent("gainFocus", self.parent.currentFocus)
			return
		elif self.next is None:
			self.previous.next = None
			self.parent.curMatrix = self.parent.firstMatrix
			self.parent.lastMatrix = self.previous
		elif self.previous is None:
			self.next.previous = None
			self.parent.firstMatrix = self.parent.curMatrix = self.next
		else:
			self.previous.next = self.next
			self.next.previous = self.previous
			self.parent.curMatrix = self.next
		#Scilently renumber all matrices
		num=self.matrixNumber
		matrix = self.next
		while matrix:
			matrix.matrixNumber = num
			num+=1
			matrix = matrix.next
		eventHandler.executeEvent("gainFocus", self.parent.curMatrix)
		del self

	def script_nextMatrix(self, gesture):
		if self.isOnlyMatrix():
			ui.message("There is only one matrix currently loaded.")
			return
		self.parent.curMatrix = (self.next if self.next else self.parent.firstMatrix)
		eventHandler.executeEvent("gainFocus", self.parent.curMatrix)
	script_nextMatrix.__doc__ = "Goes to the next matrix in the browser if possible."

	def script_previousMatrix(self, gesture):
		if self.isOnlyMatrix():
			ui.message("There is only one matrix currently loaded.")
			return
		self.parent.curMatrix = (self.previous if self.previous else self.parent.lastMatrix)
		eventHandler.executeEvent("gainFocus", self.parent.curMatrix)
	script_previousMatrix.__doc__ = "Goes to the previous matrix in the browser if possible."

	def script_reportFocus(self, gesture):
		self.reportFocus(verbose=True)

	def script_exit(self, gesture):
		eventHandler.executeEvent("gainFocus", self.parent.currentFocus)

	def script_reportLocation(self, gesture):
		self.reportFocus()

	__gestures = {
		"kb:upArrow" : "previousRow",
		"kb:downArrow" : "nextRow",
		"kb:leftArrow" : "previousColumn",
		"kb:rightArrow" : "nextColumn",
		"kb:tab" : "nextMatrix",
		"kb:shift+tab" : "previousMatrix",
		"kb:delete" : "deleteMatrix",
		"kb:nvda+tab" : "reportFocus",
		"kb:nvda+delete" : "reportLocation",
	}