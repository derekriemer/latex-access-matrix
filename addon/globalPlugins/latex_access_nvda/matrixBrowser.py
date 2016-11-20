from mathPres import MathInteractionNVDAObject
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import latex_access.matrix_processor
sys.path.remove(sys.path[-1])

class MatrixBrowserNVDAObject(MathInteractionNVDAObject):
	"""An NVDA object allowing for navigation through matrices. pressing tab and shift+tab focus the next and previous matrix."""
	
	def __init__(self, provider=None, latex=None):
		self.matrix=latex_access.matrix_processor.matrix()
		self.matrix.tex_init(latex )
		# The msg variable is here to say how many rows and columns have been initialised.
		msg = _("Initialised")
		msg = msg + str (self.matrix.rows)
		msg = msg + _(" by ")
		msg = msg + str(self.matrix.columns)
		msg = msg +_( " matrix")
		ui.message (msg)
		self.row=1
		self.column=1

	def speakMatrix(self):
		matrix=["Begin matrix",
			speech.BreakCommand(400)]
		for i in range(1, self.matrix.rows+1) :
			matrix+=self.speakRow(i)
			matrix.append(speech.BreakCommand(300))
		speech.speak(matrix+["end matrix"])

	def speakRow(self, row):
		temp = ["row "+str(row)+": ",
			speech.BreakCommand(300)]
		temp.append(speech.PitchCommand(1.25))
		for i in xrange(1,self.matrix.columns+1):
			temp+=[str(self.matrix.get_cell(row,i)), speech.BreakCommand(180)]
		temp.append(speech.PitchCommand(0.25))
		return temp

	def script_nextRow(self, gesture):
		""" Increases the row count by 1 if possible, speaking the new row, or speaks that the edge was reached. """
		if self.row == self.matrix.rows:
			ui.message("End of column.")
		else:
			self.row+=1
			ui.message (self.matrix.get_cell(self.row, self.column))

	def prevRow(self):
		"""Decreases the row count by 1 if possible, speaking the new row, or speaks that the edge was reached. """
		if self.row == 1:
			ui.message("beginning of column.")
		else:
			self.row-=1
			ui.message (self.matrix.get_cell(self.row, self.column))

	def nextColumn(self):
		""" Increases the column count by 1 if possible, speaking the new column, or speaks that the edge was reached. """
		if self.column == self.matrix.columns:
			ui.message("End of row.")
		else:
			self.column+=1
			ui.message (self.matrix.get_cell(self.row, self.column))

	def prevColumn(self):
		""" Increases the column count by 1 if possible, speaking the new column, or speaks that the edge was reached. """
		if self.column == 1:
			ui.message("Beginning of row.")
		else:
			self.column-=1
			ui.message (self.matrix.get_cell(self.row, self.column))


