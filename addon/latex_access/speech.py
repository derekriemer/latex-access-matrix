# speech.py
#    A part of the latex-access project at http://latex-access.sourceforge.net/
#    Author: Alastair Irving <alastair.irving@sjc.ox.ac.uk>
#    Modified by: Istvan Velegi <ivelegi@gmail.com>
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
'''Module to provide speech output for latex_access.'''


import latex_access
from latex_access import get_arg

#Define a list of words to use as denominators of simple fractions
denominators=[" over zero"," over1 "," half"," third"," quarter"," fifth"," sixth"," seventh"," eight"," ninth"]

class speech(latex_access.translator):
    '''Speech translator class.'''
    def __init__(self):
        latex_access.translator.__init__(self)
        self.files.append("speech.table")
        self.load_files()
        new_table={"^":self.super,"_":("<sub>","</sub>"),"\\pmod":("mod <sub>","</sub>"),"\\sqrt":self.sqrt,"\\frac":self.frac,"\\tfrac":self.frac,"\\dfrac":self.frac,"\\int":self.integral,"\\iint":self.iintegral,"\\iiint":self.iiintegral,"\\mathbf":("<bold>","</bold>"),"\\mathbb":("<bold>","</bold>"),"\\mathcal":("<mathcal>","</mathcal>"),
                   "\\log":self.log,"\\ang":self.ang,"\\tag":self.tag,"\\hat":("","hat"),"\\widehat":("","hat"),"\\bar":("","bar"),"\\overline":("","bar"),"\\dot":("","dot"),"\\ddot":("","double dot"),"\\sum":self.sum,"\\prod":self.prod,"\\bigcup":self.union,"\\bigcap":self.intersection}

        for (k,v) in new_table.iteritems():
            self.table[k]=v        
        self.space=" "
    




    def super(self,input,start):
        '''Translate  superscripts into speech.

        Returns a touple with translated string and index of
        first char after end of super.'''
        arg=get_arg(input,start)
        #Handle squared and cubed as special cases
        if arg[0] == "2":
            translation=" squared "
        elif arg[0]=="3":
            translation=" cubed "
        #Handle primes
        elif latex_access.primes.match(arg[0]):
            translation=" prime "*arg[0].count("\\prime")
        else:
            translation = " to the <sup> %s </sup> " % self.translate(arg[0])  
        return (translation,arg[1])


    def sqrt(self,input,start):
        '''Translates squareroots into speech.
        
        returns touple.'''
        opt_arg=latex_access.get_optional_arg(input, start)
        if opt_arg:
            arg=get_arg(input,opt_arg[1])
            if opt_arg[0]=="2": opt="square"
            elif opt_arg[0]=="3": opt="cube"
            elif opt_arg[0]=="": opt=""
            else: opt=opt_arg[0]+"th"
        else:
            arg=get_arg(input,start)
            opt=""
        if arg[0].isdigit() or len(arg[0])==1:
            translation="%s root %s" %(opt,arg[0])
        else:
            translation=" begin %s root %s end root" % (opt,self.translate(arg[0]))
        return (translation,arg[1])



    def frac(self,input,start):
        '''Translate fractions into speech.

        Returns touple.'''
        numerator=get_arg(input,start)
        if numerator[1]<len(input):
            denominator=get_arg(input,numerator[1])
        else:
            denominator=("",numerator[1])
        if len(numerator[0])==1 and len(denominator[0])==1:
            if numerator[0].isdigit() and denominator[0].isdigit():
                translation = numerator[0]+denominators[int(denominator[0])]
                if int(numerator[0])>1:
                    translation+="s"
                translation+=" "
            else:
                translation =" %s over %s " % (numerator[0], denominator[0])
        else:
            translation=" begin frac %s over %s end frac " % (self.translate(numerator[0]), self.translate(denominator[0]))
        return (translation,denominator[1])

    def integral(self,input,start):
        '''Translate integrals, including limits of integration.
    
        Returns touple.'''
        (lower,upper,i)=latex_access.get_subsuper(input,start)
        output=" integral "
        if lower is not None and upper is not None and len(lower[0]) !=0 and len(upper[0]) !=0:
            output+="from %s to %s of " % (self.translate(lower[0]),self.translate(upper[0]))
        elif lower is not None and len(lower[0]) !=0:
            output +="<sub>%s</sub>" % self.translate(lower[0])
        return (output,i)

    def iintegral(self,input,start):
        '''Translate double integrals, including limits of integration.
    
        Returns touple.'''
        (lower,upper,i)=latex_access.get_subsuper(input,start)
        output=" double integral "
        if lower is not None and upper is not None and len(lower[0]) !=0 and len(upper[0]) !=0:
            output+="from %s to %s of " % (self.translate(lower[0]),self.translate(upper[0]))
        elif lower is not None and len(lower[0]) !=0:
            output +="<sub>%s</sub>" % self.translate(lower[0])
        return (output,i)

    def iiintegral(self,input,start):
        '''Translate triple integrals, including limits of integration.
        
        Returns touple.'''
        (lower,upper,i)=latex_access.get_subsuper(input,start)
        output=" triple integral "
        if lower is not None and upper is not None and len(lower[0]) !=0 and len(upper[0]) !=0:
            output+="from %s to %s of " % (self.translate(lower[0]),self.translate(upper[0]))
        elif lower is not None and len(lower[0]) !=0:
            output +="<sub>%s</sub>" % self.translate(lower[0])
        return (output,i)

    def sum(self,input,start):
        '''Translate sums, including limits.
    
        Returns touple.'''
        (lower,upper,i)=latex_access.get_subsuper(input,start)
        output=" sum "
        if lower is not None and upper is not None and len(lower[0]) !=0 and len(upper[0]) !=0:
            output+="from %s to %s of " % (self.translate(lower[0]),self.translate(upper[0]))
        elif lower is not None and len(lower[0]) !=0:
            output +="<sub>%s</sub>" % self.translate(lower[0])
        return (output,i)
    
    def prod(self,input,start):
        '''Translate products, including limits of. integration.
    
        Returns touple.'''
        (lower,upper,i)=latex_access.get_subsuper(input,start)
        output=" product "
        if lower is not None and upper is not None and len(lower[0]) !=0 and len(upper[0]) !=0:
            output+="from %s to %s of " % (self.translate(lower[0]),self.translate(upper[0]))
        elif lower is not None and len(lower[0]) !=0:
            output +="<sub>%s</sub>" % self.translate(lower[0])
        return (output,i)

    def union(self,input,start):
        '''Translate unions.
    
        Returns touple.'''
        (lower,upper,i)=latex_access.get_subsuper(input,start)
        output=" union "
        if lower is not None and upper is not None and len(lower[0]) !=0 and len(upper[0]) !=0:
            output+="from %s to %s of " % (self.translate(lower[0]),self.translate(upper[0]))
        elif lower is not None and len(lower[0]) !=0:
            output +="<sub>%s</sub>" % self.translate(lower[0])
        return (output,i)

    def intersection(self,input,start):
        '''Translate intersections.
    
        Returns touple.'''
        (lower,upper,i)=latex_access.get_subsuper(input,start)
        output=" intersection "
        if lower is not None and upper is not None and len(lower[0]) !=0 and len(upper[0]) !=0:
            output+="from %s to %s of " % (self.translate(lower[0]),self.translate(upper[0]))
        elif lower is not None and len(lower[0]) !=0:
            output +="<sub>%s</sub>" % self.translate(lower[0])
        return (output,i)

    def tag(self,input,start):
        '''Translate tags into speech.

        Returns a touple with translated string and index of
        first char after end of tag.'''

        arg=get_arg(input,start)
        translation=" tag left paren "+arg[0]+" right paren "
        return (translation,arg[1])

    def ang(self,input,start):
        '''Translate angles into speech.

        Returns a touple with translated string and index of
        first char after end of angle.'''

        translation = ""
        counter = 0
        arg=get_arg(input,start)
        if ';' in arg[0]: # we have mins possibly seconds too
            for x in arg[0]:
                if ';' == x: # we have mins/sec
                    counter=counter+1
                    if counter == 1:
                        translation=translation+" degrees "
                        continue
                    elif counter == 2:
                        translation=translation+" minutes "
                        continue
                    elif counter == 3:
                        translation=translation+" seconds "
                        continue 
                translation=translation+x
            if counter == 1:
                translation=translation+" minutes"
            elif counter == 2:
                translation=translation+" seconds"
        else:
            translation=arg[0]+" degrees"
        return (translation,arg[1])

    def log(self,input,start):
        '''Translate logs into speech.

        We translate logs in the form \log_a(x) as
        log base a of x

        If the log appaears ambiguous, i.e. we can not reasonably
        determine the base, we shall translate as just "log" followed by
        any usual translation.
        
        Returns a touple with translated string and index of
        first char after end of entire logarithm.'''

        log=get_arg(input,start)
        translation=" log "
        if len(log[0]) < 1 or log[0][0] != "_": # \log by itself 
            return (translation, log[2]) # ignore the supposed command 

# Safe to assume log is of the form \log_a(x)
        translation+="base "
        base=get_arg(input, log[1])
        translation+=self.translate (base[0])
        translation+=" of "
        return (translation, base[1])
    
