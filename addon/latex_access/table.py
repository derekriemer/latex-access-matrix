#    table.py
#    A part of the latex-access project at http://latex-access.sourceforge.net/
#    Author: Daniel Dalton <daniel.dalton10@gmail.com>
#    Copyright (C) 2011,2012 Daniel Dalton/latex-access Contributors
#
#    This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation;
#    either version 2 of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#    See the GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along with this program; if not, visit <http://www.gnu.org/licenses>

# How it works -- brief overview to help developers implement for other
# screenreaders/editors etc.
# The WhereAmI function is ultimately the one that should be called to
# do all the work, at the end of the day it returns the nicely formatted
# string ready to be passed to the speech synthesiser.
# Inorder to do this, you must supply WhereAmI with a few arguments:
# WhereAmI(GetTableCurrentRow(table), BuildHeaderString(GetTableTopRow (table)))
# Is the basic form to call this -- table is just the text of the table
# you are working with.
# The boundaries of table should be from the first character of the
# first cell in table, that is the top row, left hand cell, first char
# is the point at which the table should begin, and the end of the input
# passed to this module should be where point resides (hopefully in the
# table somewhere.
# Marking from the end of the \begin{tabular} line should be ok as
# well.
#
# It may be wise to do some validation checks before passing table to
# this module i.e. check cursor is actually inside table, otherwise, I
# predict (without testing), you'll get out of list index errors thrown
# from python, or it'll just say your in the last column... Which is not
# what we want!
# Enjoy.

"""Latex-access table accessibility.

This module provides a range of functions to grab particular information
from a LaTeX tabular environment, providing useful information to the
document author when working with tables."""

if __name__ == "__main__":
  print "This can only be used as a module, and does nothing when called interactively."
  exit (-1)
  
def BuildHeaderString (text):
  """Create a tupple of headings.

  These headings will be spoken when queried.
  Provide the first row of a table which should represent the column
  headings. This should be of type string(str)."""

  tableheadings = [] # define an empty list
  text = text.replace("\hline", "") # remove any hline, though there
  # should only be one at most.
  text = text.replace("\n", "") # So we don't miss last col
  text = text.replace("\\\\", "") 
  text = text+"&" # Don't miss the last column 
  while text.find("&") != -1: # column LaTeX separater
    tableheadings.append(text[:text.find("&")]) # next remove last col
    text = text[text.find("&")+1:] # remove last col and separator

  return tableheadings # return list of column headings.

def WhereAmI (row, headers, table):
  """Provides information of current location in table.

  Currently speak the name of column and cell position within table.
  row should be a string object containing the current row, and headers
  should be a list of the table headings (as returned by BuildHeaderString..."""

  try:
    out="focus is in column "+headers[row.count("&")] # Count how many
# columns across we are and return corresponding heading. (by counting
# col separater &)
# cell location/position
    out=out+" at location "+GetTablePosition(table,row)
  except IndexError:
    out="outside table"

  return out 

def GetTableTopRow (table):
  """Return the first row of a table.

  This is useful for separating the row headings from the rest of the
  stuff in the table. table should just be an object type str holding
  the contents of the LaTeX table up until cursor or (point)."""

  return table[:table.find("\\\\")]

def GetTableCurrentRow (table):
  """Return the currently focused row in table.

  Find the last \\ char from end of  input. Everything between end [-1],
  and the last \\ char is considered the current row. table should be of
  type str and is the contents of the LaTeX table up until the cursor or
  (point)."""

  return table[table.rfind("\\\\")+1:].replace("\n", "").replace("\\hline",
                                                               "") 
def GetTablePosition (table,currrow):
  """Get the current row  and cell location as a coordinate.

  table should be contents of table from the beginning of table up until
  the cursor, row should be an str object of the currently focused row."""

# \\ represents a newline in latex and hence a new row. & is the LaTeX
# column separater. Hence, do the counting.
  row=table.count("\\\\") # number of rows?
  column=currrow.count("&") # number of columns

# Next calculate letter coordinates for the column
# Currently supports only 26*26+26=702 columns
# define the alphabet
  alph=("A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z")
  position = "" # Null to begin 
  if column >= 26: # Need two letter column identification 
    position=position+alph[(column/26)-1] 
    position=position+" "+alph[column%26]
  else: # less than 26 cols (one letter identifier)
    position=position+alph[column]

# The rows much more straight forward!
  position=position+" "+str(table.count("\\\\")+1) # header is row 1 
  return position # cell position 
