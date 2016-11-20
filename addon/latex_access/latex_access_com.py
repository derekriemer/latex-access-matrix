# latex_access_com.py
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
#This file defines a com object wihch can be used to interface between 
#screenreaders and the latex access scripts


import preprocessor
import speech
import settings
import os

class latex_access_com:
    def __init__(self):
        self.filename = os.path.join(os.path.expandvars("%appdata%"), "latex-access.conf")
        self.speech_translator=speech.speech()
        self.preprocessor=preprocessor.preprocessor()
        self.activateSettings()
        self.newcommands=preprocessor.newcommands(self.preprocessor)
    _reg_progid_ = "latex_access"
    _public_methods_ =["nemeth","speech","preprocessor_add","preprocessor_from_string","preprocessor_write","preprocessor_read","toggle_dollars_nemeth","toggle_dollars_speech", "activateSettings"]
    def nemeth(self, input):
        '''Translates the input into Nemeth Braille.'''
        input=self.preprocessor.translate(input)
        return self.nemeth_translator.translate(input)
    
    def speech(self,input):
        '''Translates the input into english speech.'''
        input=self.preprocessor.translate(input)
        return self.speech_translator.translate(input)

    def toggle_dollars_nemeth(self):
        '''Toggles whether dollars are shown in braille.

        Returns a boolian of whether dollars are being removed.'''
        self.nemeth_translator.remove_dollars=not self.nemeth_translator.remove_dollars
        return self.nemeth_translator.remove_dollars

    def toggle_dollars_speech(self):
        '''Toggles whether dollars are spoken 

        Returns a boolian of whether dollars are being removed.'''
        self.speech_translator.remove_dollars=not self.speech_translator.remove_dollars
        return self.speech_translator.remove_dollars

    def preprocessor_add(self,command,args,translation_string):
        '''A function to add entries to the preprocessor'''

        self.preprocessor.add_from_string(command,args,translation_string)

    def preprocessor_from_string(self,input):
        '''Adds preprocessor entries from a LaTeX string containing \newcommand.'''
        self.newcommands.translate(input)

    def preprocessor_write(self, filename):
        self.preprocessor.write(filename)

    def preprocessor_read(self, filename):
        self.preprocessor.read(filename)

    def activateSettings (self):
        """Activate the latex-access settings stored in file.

        Consult the actual function definition in settings.py for details
        and documentation."""
        settings.loadSettings (os.path.expanduser(self.filename))
        self.nemeth_translator=settings.brailleTableToUse ()
        return settings.activateSettings ({"braille":self.nemeth_translator,"speak":self.speech_translator,"preprocessor":self.preprocessor})

#Register the object
if __name__=='__main__':
    import pythoncom,win32com.server.register
    latex_access_com._reg_clsid_=pythoncom.CreateGuid()
    latex_access_com._reg_clsctx_=pythoncom.CLSCTX_LOCAL_SERVER 
    win32com.server.register.UseCommandLine(latex_access_com)
