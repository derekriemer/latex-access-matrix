# nemeth.py
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
'''Module to provide Nemeth translations for the latex_access
module.'''


import latex_access
from latex_access import get_arg

class nemeth(latex_access.translator):
    '''Class for nemeth translations.'''

    def __init__(self):
        latex_access.translator.__init__(self)
        self.files.append("nemeth.table")
        self.load_files()
        new_table={"\\dot":("","`"),"\\ddot":("","``"),
                   "^":self.super,"_":self.sub,"\\sqrt":self.sqrt,"\\frac":self.frac,"\\dfrac":self.frac,"\\tfrac":self.frac,
                   "\\tag":self.tag,"\\mathbf":("_",""),"\\mathbb":("_",""),"\\colvec":("{"," ","o"),"\\tcolvec":("{"," "," ","o"),"\\bar":self.bar,"\\hat":self.bar,"\\widehat":self.bar,"\\overline":self.bar}

        # The upper case ascii letters
        for letter in range (65,91):
            new_table["%c" % (letter)] = self.upperLetter
            
        for (k,v) in new_table.iteritems():
            self.table[k]=v






    def super(self,input,start,rting=()):
        '''Translate  superscripts into Nemeth.

        Returns a touple with translated string and index of
        first char after end of super.'''
        arg=get_arg(input,start)
        #Handle squared and cubed as special cases
        if arg[0] == "2":
            translation="<"
        elif arg[0]=="3":
            translation="%"
        #Handle primes
        elif latex_access.primes.match(arg[0]):
            translation="'"*arg[0].count("\\prime")
        else:
            if rting==():
                translation = "~" + self.translate(arg[0]) + "\""
            else:
                                translation = "~" + self.translate(arg[0],(rting[0]+arg[2],rting[1]+1)) + "\""
        return (translation,arg[1])



    def sub(self,input,start,rting=()):
        '''Translates nemeth subscripts.

        Returns a touple, as above'''
        arg=get_arg(input,start)
        if arg[0].isdigit():
            translation=arg[0]
            if rting!=():
                for j in range(len(arg[0])): self.rt.append((rting[1]+j,rting[0]+arg[2]+j))
        else:
            if rting==():
                translation = ";"+self.translate(arg[0]) + "\""
            else:
                translation = ";"+self.translate(arg[0],(rting[0]+arg[2],rting[1]+1)) + "\""
        return (translation,arg[1])

    def sqrt(self,input,start,rting=()):
        '''Translatesroots in latex.

        Returns a touple as above.'''
        arg=get_arg(input,start)
        if arg[0].isdigit() or len(arg[0])==1:
            translation=">"+arg[0]
            if rting!=():
                for j in range(len(arg[0])): self.rt.append((rting[1]+1+j,rting[0]+arg[2]+j))
        else:
            if rting!=(): translation=">"+self.translate(arg[0],(rting[0]+arg[2],rting[1]+1))+"}"
            else: translation=">"+self.translate(arg[0])+"}"
        return (translation,arg[1])

    def frac(self,input,start,rting=()):
        '''Translates fractions into Nemeth.

        Returns touple as above'''
        numerator=get_arg(input,start)
        if numerator[1]<len(input):
            denominator=get_arg(input,numerator[1])
        else:
            denominator=("",numerator[1],numerator[1])
        if numerator[0].isdigit() and denominator[0].isdigit():
            translation=numerator[0]+"/"+denominator[0]
            if rting!=():
                for j in range(len(numerator[0])): self.rt.append((rting[1]+j,rting[0]+numerator[2]+j))
                for j in range(len(denominator[0])): self.rt.append((rting[1]+j+1+len(numerator[0]),rting[0]+denominator[2]+j))
        else:
            if rting==():
                translation="?"+self.translate(numerator[0])+"/"+self.translate(denominator[0])+"#"
            else:
                transnum=self.translate(numerator[0],(rting[0]+numerator[2],rting[1]+1))
                transden=self.translate(denominator[0],(rting[0]+denominator[2],rting[1]+len(transnum)+2))
                translation="?"+transum+"/"+transden+"#"
        return (translation,denominator[1])


    def bar(self, input, start,rting=()):
        '''Handles bar/overline.

        Returns toutple'''
        arg=get_arg(input,start)
        if len(arg[0])==1:
            translation=":%s" % arg[0]
            if rting!=(): self.rt.append((rting[1]+1,rting[0]+arg[2]))
        else:
            if rting==(): translation=":{%so" % self.translate(arg[0])
            else: translation=":{%so" % self.translate(arg[0],(rting[0]+arg[2],rting[1]+2))
        return (translation,arg[1])

    def tag(self,input,start):
        '''Translate  tags into Nemeth.

        Returns a touple with translated string and index of
        first char after end of tag.'''
        arg=get_arg(input,start)
        translation="  {"+arg[0]+"}"
        return (translation,arg[1])

    def upperLetter (self, input, start):
        '''Translates upper case letters in latex.

        Returns a touple as above.'''
        if self.capitalisation == '8dot':
            return (input[start-1], start)
        start=start-1 # We are focused on current char 
        translation= "" # The brf translation 
        cap = True # Provide a capital sign unless special case (below)
#        doublecap = False # Do we represent consecutive capital letters by ,,
#        try: # Letter before wasn't a cap, but letter after is so start consecutive capitals (,,)
#            if input[start+1].isupper () and not input[start-1].isupper ():
#                doublecap = True
#                cap = False # And no need for single , 
#        except:
#            pass
#        try: # Handle double Cap on start of line 
#            if start == 0 and input[start+1].isupper ():
#                doublecap = True
#                cap = False # No single cap necessary 
#        except:
#            pass
#        try: # the double ,, has already been provided for this set of consecutive capital letters 
#            if start > 0 and input[start-1].isupper ():
#                cap = False
#                doublecap =False
#        except:
#            pass
        if start == 0: # Handle cap at start of line 
            cap = True
#        if doublecap: # we add double capital sign 
#            translation += ',,'
        if cap: # Otherwise just add single cap sign 
            translation += ','
        translation+=input[start].lower () # Now add the lowercase equivilant to avoid dot 7 in some tables 
        return (translation, start+1)
