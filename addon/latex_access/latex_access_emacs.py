#!/usr/bin/python

# latex_access_emacs.py
#    A part of the latex-access project at http://latex-access.sourceforge.net/
#    Author: Daniel Dalton <daniel.dalton10@gmail.com>
#    Copyright (C) 2011,2012,2013 Daniel Dalton/latex-access Contributors
#
#    This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation;
#    either version 2 of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#    See the GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along with this program; if not, visit <http://www.gnu.org/licenses>
#
# A silly hack, so we don't need to worry about classes to access the
# translate functions.
# Used for communication via pyymacs from within emacs.
# Written by Daniel Dalton <daniel.dalton10@gmail.com>

"""Silly hack to access translate functions as pymacs was difficult to
interact with classes."""

import sys
import os.path
import settings
import speech
import nemeth
import ueb
import preprocessor
import matrix_processor
import table as t

s=speech.speech()
n=''
p=preprocessor.preprocessor()
nc=preprocessor.newcommands(p)
matrix=matrix_processor.matrix ()
matrix.row=1
matrix.column=1

if __name__ == "__main__":
    print "This is just a module."
    exit (-1)

def activateSettings ():
    """Activate the latex-access settings stored in file.

    Consult the actual function definition in settings.py for details
    and documentation."""
    global n # handle to the braille translator
    # Paths pointing to potential configuration files.
    configFilePaths=(os.path.expanduser("~/.latex-access"), "/etc/latex-access.conf")
    for configFile in configFilePaths:
        if os.path.exists (configFile):
            break

    settings.loadSettings (configFile)
    n=settings.brailleTableToUse ()
    return settings.activateSettings ({"braille":n,"speak":s,"preprocessor":p})

def transbrl (arg):
    """Translate latex code into Nemeth Braile.

    Unless you are using pymacs to call this, please use the function
    nemeth.nemeth.translate() instead. Found in nemeth.py."""
    return n.translate(p.translate(arg))

def transsp (arg):
    """Translate a line of LaTeX source into understandable speech.

    Unless calling with pymacs, please use
    speech.speech.translate(). Found in speech.py."""

    return s.translate(p.translate(arg))

def toggle_dollars_speech ():
    """Toggle the speaking of dollar signs.

    This functions is here to negotiate the class, so that pymacs isn't
    able to cause us trouble."""
    s.remove_dollars=not s.remove_dollars
    return s.remove_dollars

def preprocessor_add(command,args,translation_string):
    '''A function to add entries to the preprocessor'''
    p.add_from_string(command,args,translation_string)

def preprocessor_from_string(input):
    '''Adds preprocessor entries from a LaTeX string containing \newcommand.'''
    nc.translate(input)

def preprocessor_write(filename):
    p.write(filename)

def preprocessor_read(filename):
    p.read(filename)

# Export the table.* functions to emacs.
def BuildHeaderString (text):
    """Enable access to the BuildHeaderString function for table
    manipulation.

    Consult the documentation in table.py."""

    return t.BuildHeaderString (text)

def WhereAmI (row, headers,table):
    """Access to the WhereAmI function in table.py.

    This exports the WhereAmI function to emacs -- consult documentation
    in table.py for more details."""

    return t.WhereAmI (row, headers,table)

def GetTableTopRow (latextable):
    """Make the GetTopRow function available to emacs for table
    manipulation.

    Consult the documentation in table.py for details."""

    return t.GetTableTopRow (latextable)

def GetTableCurrentRow (latextable):
    """Get the current row of a table.

    Export this function to emacs so to allow for latex table
    accessibility."""

    return t.GetTableCurrentRow (latextable)

# The matrix functions.
def matrixUp ():
    if matrix.row == 1:
        return "top of matrix"
    else:
        matrix.row-=1
        return matrix.get_cell(matrix.row,matrix.column)

def matrixDown ():
    if matrix.row >= matrix.rows:
        return "bottom of matrix"
    else:
        matrix.row+=1
        return matrix.get_cell(matrix.row,matrix.column)

def matrixLeft ():
    if matrix.column <= 1:
        return "first cell"
    else:
        matrix.column-=1
        return matrix.get_cell(matrix.row,matrix.column)

def matrixRight ():
    if matrix.column >= matrix.columns:
        return "last cell"
    else:
        matrix.column+=1
        return matrix.get_cell(matrix.row,matrix.column)

def matrixGoto (row,column):
    # Check that the row and column is valid
    if row in range (1,matrix.rows+1) and column in range (1,matrix.columns+1):
        matrix.row = row
        matrix.column = column
        return matrix.get_cell (matrix.row, matrix.column)
    else:
        return "invalid cell"

def matrixInit (region):
    matrix.row=matrix.column=1
    return matrix.tex_init (region)
