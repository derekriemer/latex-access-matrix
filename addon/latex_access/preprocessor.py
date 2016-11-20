# preprocessor.py
#    A part of the latex-access project at http://latex-access.sourceforge.net/
#    Author: Alastair Irving <alastair.irving@sjc.ox.ac.uk>
#    Copyright (C) 2011 Alastair Irving/latex-access Contributors
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
'''This module provides a translator which can be used to replace LaTeX in the input with different LaTeX.

For example it can be used to handle commands defined by \newcommand.'''

import cPickle as pickle
import latex_access


class preprocessor(latex_access.translator):
    '''Preprocessor translator

    All translations done by this translator should use the general_command mechanism rather than custom functions.'''
    def __init__(self):
        latex_access.translator.__init__(self)        
        self.table={}

    def add(self,command,translation):
        '''Add a translation to the table.'''
        self.table[command]=translation

    def add_from_string(self, command, args, translation_string):
        '''This adds a command to the preprocessor given its number of arguments as well as its output in the form of an argument to \newcommand.

        Therefore the final argument is a string using #n to denote the nth argument.'''
        translation=[]
        translation.append(args)
        l=translation_string.split("#")
        translation.append(l[0])
        for s in l[1:]:
            translation.append(int(s[0]))
            translation.append(s[1:])
        self.table[command]=translation

    def write(self, filename):
        '''Saves the preprocessor entries to a file.'''
        f=open(filename,"w")
        pickle.dump(self.table,f)
        f.close()

    def read(self, filename):
        '''Reads preprocessor entries from a file and appends them to the dictionary.'''
        f=open(filename)
        newtable=pickle.load(f)
        f.close()
        for (k,v) in newtable.iteritems():
            self.table[k]=v

class newcommands(latex_access.translator):
    '''Provides a translator to extract all \newcommand commands from a string.'''
    def __init__(self,preprocessor):
        latex_access.translator.__init__(self)
        self.table={"\\newcommand":self.newcommand,"\\renewcommand":self.newcommand}
        self.preprocessor=preprocessor
        
    def newcommand(self, input, start):
        command=latex_access.get_arg(input,start)
        args=latex_access.get_optional_arg(input,command[1])
        if args:
            start=args[1]
            args=int(args[0])
        else:
            args=0
            start=command[1]
        translation=latex_access.get_arg(input,start)
        self.preprocessor.add_from_string(command[0],args,translation[0])
        return ("",translation[1])
    

