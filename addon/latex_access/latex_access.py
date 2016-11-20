# latex_access.py
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

'''This module provides translations of lines of LaTeX into either braille or spoken output.'''

import re
import types
import os.path
from path import get_path
import codecs
import routing

# Regular expression to match LaTeX commands
latex_command=re.compile(r"\\(([a-zA-Z]+)|[,!;\{\}\[\];:])")
#Regexp for testing if a string contains only primes
primes=re.compile(r"^\s*(\\prime\s*)+$")


class translator:
    '''Class from which all translators will inherit.'''
    def __init__(self):
        self.depth=0
        self.table={"$":self.dollar,
                    "\\mbox":self.text,"\\text":self.text,"\\textrm":self.text,"\\textit":self.text,"\\mathrm":self.text,"\\textbf":self.text,"\\displaystyle":self.displaystyle,"\\phantom":self.remove,"\\index":self.remove,"\\hspace":self.remove,"\\vspace":self.remove}
        
        self.remove_dollars=False
        self.space=""
        self.files=[]

    def load_file(self,filename):
        '''Loads simple string table entries from a file.

        The file is a simple text file, lines beginning with ; are ignored.
        Other lines are split at the first space into a command and translation.'''
        f=codecs.open(os.path.join(get_path(),filename),"r","utf-8")
        for l in f.readlines():
            if l[0]==";" or l[0]=="\n": continue
            words=l.split(" ")
            self.table[words[0]]=(" ".join(words[1:])).strip("\r\n")
        f.close()

    def load_files(self):
        [self.load_file(f) for f in self.files]
    
    def translate(self,input,rting=()):        
        '''This translates the string in input using the translation table

        Returns string.'''
        if self.depth==0:
            if hasattr (self, "before"):
                self.before ()
            self.rt=[] #Routing table
            rting=(0,0)
            backupPosition = 0
            rtlen = 0
            self.expandItem = hasattr(self, "expandCurrentWord") and self.expandCurrentWord and hasattr(self, "cursorOffset")
            firstRun = True
            snipCommand = False 
        self.depth+=1

        consumed=0
        expandUntil = -1
        output=""
        i=0
        while True:
            if self.expandItem and (self.depth == 1):
              if expandUntil >= 0:
                if i == expandUntil:
                  expandUntil = -1
              else:
                if (self.cursorOffset >= consumed) and (self.cursorOffset < i):
                  expandUntil = i
                  i = consumed
                  output = output[:backupPosition]
                  self.rt = self.rt[0:rtlen]

            brfOutChars=len(output)
            if self.depth == 1 and firstRun and brfOutChars > 0:
                firstRun = False
                if hasattr (self, "displayLength") and brfOutChars > self.displayLength:
                    snipCommand = True
                    break
                
            if hasattr (self, "displayLength"):
                if brfOutChars > self.displayLength: # we have exceeded the display so go back to the last good contraction
                    output=output[:backupPosition]
                    break

            backupPosition=brfOutChars # remember where our last good contraction is
            consumed=i

            if rting!=():
                self.rt.append((len(output)+rting[1],i+rting[0]))
            rtlen = len(self.rt)

            if hasattr (self, "displayLength"):
                if brfOutChars == self.displayLength: # translation exactly the size of the display, break
                    break

            if i == len(input):
                break

            if expandUntil >= 0:
              output += input[i]
              i += 1
              continue

            # Test if we have a LaTeX command
            if input[i] == "\\":
                match=latex_command.match(input[i:])
                if match:
                    curr=match.group()
                else:
                    curr="\\"
                    
            else:
                curr=input[i]
                
            if curr in self.table:
                i+=len(curr)
                result=self.table[curr]
                if type(result) in (types.StringType,types.UnicodeType):
                    output+=self.space
                    output += result
                    output+=self.space
                elif type(result)==types.TupleType or type(result)==types.ListType:
                    if rting==(): translation=self.general_command(input,i,result)
                    else: translation=self.general_command(input,i,result,(rting[0],rting[1]+len(output)))
                    output+=translation[0]
                    i=translation[1]                    
                elif type(result) == types.MethodType:
                    if rting!=():
                        try: translation=result(input,i,(rting[0],rting[1]+len(output)))
                        except: translation=result(input,i)
                    else:
                        translation=result(input,i)
                    output+=translation[0]
                    i=translation[1]
            

            else:
                output += curr
                i += len(curr)
        self.depth-=1
        if self.depth==0:
            self.consumedChars=consumed
            self.trans2src=routing.convert(self.rt)
            self.src2trans=routing.convert(routing.invert(self.rt))
            if snipCommand:
                output=output[:self.displayLength]
                self.consumedChars = self.trans2src[self.displayLength]
        return output

    def text(self,input, start,rting=()):
        '''Used to translate text, as in mbox and text

        returns tuple.'''
        arg=get_arg(input,start)
        if rting==():
            translation = self.translate (arg[0])
        else:
                        translation = self.translate (arg[0],(rting[0]+arg[2],rting[1]))
        return (translation,arg[1])

    def displaystyle(self,input, start):
        '''Removes the displaystile command but translates its argument.

        Returns tuple.'''
        i=start
        #Check we haven't gone past the end of the command
        if i>=len(input): return ("",i)
        #Skip space
        while input[i]==" " and i < len(input): i+=1
        if input[i]=="{":
            arg=get_arg(input,start)
            return (self.translate(arg[0]),arg[1])
        else:
            return("",i)
    
    def remove(self,input,start):
        '''Used to remove a command and its argument totally from the translation.
        Useful for phantom commands.  

        Returns tuple.'''
        arg=get_arg(input,start)
        return("",arg[1])


    def general_command(self,input, start, delimitors,rting=()):
        '''Used to process a command when the required translation is just the arguments joined by appropriate delimitors. 
        The 3rd argument is a list of such delimitors, the 1st element of which goes before the 1st argument of the command, etc.
        Alternatively, if the 1st element is a number then it is interpreted as the number of arguments and subsequent arguments are treated as follows:
        A string is treated as a delimitor 
        An integer refers to the corresponding argument which is translated and inserted into the string.

        Returns usual tuple.'''
        if type(delimitors[0])==types.StringType:
            translation=self.space
            translation+=delimitors[0]
            translation+=self.space
            for delim  in delimitors[1:]:
                arg=get_arg(input,start)
                if rting==(): translation+=self.translate(arg[0])
                else: translation+=self.translate(arg[0],(rting[0]+arg[2],rting[1]+len(translation)))
                translation+=self.space
                translation+=delim
                translation+=self.space
                start=arg[1]
        else:
            arguments=[]
            for i in range(0,delimitors[0]):
                arg=get_arg(input,start)
                arguments.append(arg[0])
                start=arg[1]
            translation=self.space
            for x in delimitors[1:]:
                if type(x) in (types.StringType,types.UnicodeType):
                    translation+=x
                    translation+=self.space
                else:
                    translation+=self.translate(arguments[x-1])
                    translation+=self.space

        return (translation,start)

    def dollar(self,input,start):
        '''Handles dollars, either ignoring or removing them.
    
        Returns tuple.'''
        if (self.remove_dollars):
            translation=""
        else:
            translation="$"
        return (translation, start)


def get_arg(input,start):
    '''Returns the argument of a latex command, starting at start.
        
    Returns a tuple containing the contents of the argument
    and the index of the next character after the argument
    and the place where the argument actually st.arts'''
    i=start
    #Check we haven't gone past the end of the command
    if i>=len(input) or input[i:].isspace (): return ("",i,i)
    #Skip space
    while (i < len(input)) and (input[i] == " "):
        i+=1
    #Handle unbraced LaTeX commands
    if input[i] == "\\":
        actual_start=i
        match=latex_command.match(input[i:])
        if (match):
            arg=match.group()
            i+=len(arg)
        else:
            arg="\\"
            i+=1
        return (arg,i,actual_start)
    if input[i] != "{":
        return (input[i],i+1,i)
    else:
        i+=1
        actual_start=i        
        start=i
        j=1 #Variable to track nested braces
        while (j != 0) and i < len(input):
            if input[i] == "{":
                j+=1
            if input[i] == "}":
                j-=1
            i+=1
        #This is a hack to avoid problems when the braces haven't yet been closed
#        if input[i-1]!="}":
#            i+=1
        if input[i-1]=="}":
            return(input[start:i-1],i,actual_start)
        else:
            return(input[start:i],i,actual_start)

def get_optional_arg(input,start):
    '''Returns the optional argument of a latex command, if it exists, starting at start.
        
    Returns a tuple containing the contents of the argument
    and the index of the next character after the argument, and an empty tuple if no argument is found.'''
    i=start
    if i>=len(input): return ()
    #Skip space
    while input[i]==" " and i < len(input):
        i+=1
    if input[i] != "[":
        return ()
    else:
        i+=1
        start=i
        j=1 #Variable to track nested brackets
        while j!=0 and i < len(input):
            if input[i] == "[":
                j+=1
            elif input[i] == "]":
                j-=1
            i+=1
        #This is a hack to avoid problems when the brackets haven't yet been closed
        if input[i-1]!="]":
            i+=1
        return(input[start:i-1],i)

def get_subsuper(input,start):
    '''Function to handle cases where we may have some combination of a super and a sub, for example in limits of integrals and sums.

    Returns tupple (sub,super,i)'''
#This code was copied from a function for integrals, so lower means sub and upper means super.
    lower=None
    upper=None
    i=start
    if i>=len(input): return (lower,upper,i)
    while input[i]==" " and i < len(input):
        i+=1
    if input[i]=="_":
        lower=get_arg(input,i+1)
        i=lower[1]            
        if i < len(input):
            while input[i]==" " and i < len(input):
                i+=1
            if input[i]=="^":
                upper=get_arg(input,i+1)
                i=upper[1]
        #Now repeat this the other way round in case upper limit comes first
    elif input[i]=="^":
        upper=get_arg(input,i+1)
        i=upper[1]
        if i < len(input):
            while input[i]==" " and i < len(input):
                i+=1
            if input[i]=="_":
                lower=get_arg(input,i+1)
                i=lower[1]    
    return (lower,upper,i)

