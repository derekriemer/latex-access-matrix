# routing.py
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

'''This module provides functions for manipulating routing information.'''

def convert(rt):
    '''Given an rt which is an incomplete  list of tupples create a flat list.'''
    if rt==[]: return []
    new=[]
    for i in range(len(rt)-1):
        a=rt[i]
        b=rt[i+1]
        for j in range(a[0],b[0]):
            new.append(a[1]) #This maybe will be better as a linear interpolation
    new.append(rt[-1][1])
    return new
            
    
def invert(rt):
    '''Invert the tupples in an rt.'''
    return [(i[1],i[0]) for i in rt]
