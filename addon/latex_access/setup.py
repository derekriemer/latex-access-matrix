# setup.py
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
from distutils.core import setup
import py2exe
import sys

class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)

                    
latex_access_com= Target(description="latex_access com server",
name="latex_access_com",
                    modules=["latex_access_com"],
                    create_exe = False,
                    create_dll = True)
                    
                    
latex_access_matrix= Target(description="latex_access matrix com server",
name="latex_access_matrix",
                    modules=["matrix_processor"],
                    create_exe = False,
                    create_dll = True)
                    
                    
setup (
                    com_server=[latex_access_com,latex_access_matrix])





