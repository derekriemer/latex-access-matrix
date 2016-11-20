# -*- coding: utf8 -*-
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
import re

#Define a list of words to use as denominators of simple fractions
denominators=[" over zero"," over1 "," half"," third"," quarter"," fifth"," sixth"," seventh"," eight"," ninth"]

sqrt_with_two_args =re.compile(r".*\\sqrt\[(.?)\]")

class speech(latex_access.translator):
    '''Speech translator class.'''
    def __init__(self):
        latex_access.translator.__init__(self)
        self.files.append("speech.table")
        self.load_files()
        new_table ={"\\cap":self.cap,"\\bigcap":self.cap, "\\ln":self.ln,"\\binom":self.binom,"\\vec":self.vect,"^":self.super,"_":("<sub>","</sub>"),"\\pmod":("mod <sub>","</sub>"),
                "\\sqrt":self.sqrt,"\\frac":self.frac,"\\tfrac":self.frac,"\\dfrac":self.frac,
                "\\int":self.integral,"\\dbint":self.dbintegral,"\\ddint":self.ddintegral,"\\oint":self.ointegral,
                "\\it":("<it>","</it>"),"\\bf":("<bold>","</bold>"),"\\mathbf":("<bold>","</bold>"),"\\mathbb":("<bold>","</bold>"),
                "\\mathcal":("<mathcal>","</mathcal>"),"\\log":self.log,"\\ang":self.ang,
                "\\tag":self.tag,"\\hat":("","hat"),"\\widehat":("","hat"),"\\bar":("","bar"),
                "\\overline":("","bar"),"\\dot":("","dot"),"\\ddot":("","double dot"),"\\sum":self.sum,"\\prod":self.prod,"\\cup":self.union,"\\bigcup":self.union}
        
        for (k,v) in new_table.iteritems():
            self.table[k]=v
        self.space=" "
        
    sqrt_with_two_args =re.compile(r".*\\sqrt\[(.*)\]+.*")
    
    def correct(self, inputstr):
        inputstr =inputstr.replace("xy", "x y")
        inputstr =inputstr.replace("yx", "y x")
        inputstr =inputstr.replace("yy", "y y")
        inputstr =inputstr.replace("ix", "i x")
        inputstr =inputstr.replace("imx", "i m x")
        inputstr =inputstr.replace("ikx", "i k x")
        inputstr =inputstr.replace("isx", "i es x")
        inputstr =inputstr.replace("inx", "i n x")
        return inputstr
    

    def super(self,input,start):
        '''Translate  superscripts into speech.

        Returns a touple with translated string and index of
        first char after end of super.'''
        
        arg_with_minus =re.compile(r"-.?")
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
            translation = " to the <sup> %s </sup> " % self.correct(self.translate(arg[0]))  
        return (translation,arg[1])

    def sqrt(self,input,start):
        '''Translates roots into speech.
        returns touple.'''
        
        if self.sqrt_with_two_args.match(input):
            first_arg =latex_access.get_optional_arg(input, start)
            second_arg=get_arg(input, first_arg[1])
            
            if first_arg[0] =="2":
                translation =u" square "
            elif first_arg[0] =="3":
                translation =u" cube "
            elif first_arg[0].lower() =="n":
                translation =u"enth "
            elif first_arg[0].lower() =="x":
                translation =u"exth "
            elif first_arg[0] =="":
                translation =u""
            else:
                translation =first_arg[0] +u"th "
                
            if len(second_arg[0]) ==1:
                translation +=u"root " +self.correct(self.translate(second_arg[0]))
            else:
                translation +=u"root of " +self.correct(self.translate(second_arg[0]))
                translation +=u" end root "
            return (translation,second_arg[1])

        arg=get_arg(input,start)
        if arg[0].isdigit() or len(arg[0])==1:
            translation =u" root " +arg[0] +u" "
        else:
            translation =u" root of " +self.correct(self.translate(arg[0])) +u" end root "
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
            translation=" begin frac, %s over %s, end frac " % (self.translate(numerator[0]), self.translate(denominator[0]))
        return (translation,denominator[1])

    def dsfrac(self,input,start):
        arg=get_arg(input,start)
        translation=u" begin frac "+self.correct(self.translate(arg[0])) +u" end frac "
        return (translation,arg[1])

    def integral(self,input,start):
        '''Translate integrals, including limits of integration.
        Returns touple.'''
        
        (lower,upper,i)=latex_access.get_subsuper(input,start)
        output =u" integral "
        
        # Statement to prevent the translator from empty boundaries:
        if lower is not None and upper is not None and len(lower[0]) !=0 and len(upper[0]) !=0:
            output +=" from "
            output +=self.correct(self.translate(lower[0]))
            output +=" to "
            output +=self.correct(self.translate(upper[0]))
            output +=" of "
        elif lower is not None and len(lower[0]) !=0:
                output +="<sub>"+self.correct(self.translate(lower[0]))+"</sub>"
        return (output,i)

    def dbintegral(self,input,start):
        '''Translate double integrals, including limits of integration.
        Returns touple.'''
        
        (lower,upper,i)=latex_access.get_subsuper(input,start)
        output =u" double integral "
        
        # Statement to prevent the translator from empty boundaries:
        if lower is not None and upper is not None and len(lower[0]) !=0 and len(upper[0]) !=0:
            output +=" from "
            output +=self.correct(self.translate(lower[0]))
            output +=" to "
            output +=self.correct(self.translate(upper[0]))
            output +=" of "
        elif lower is not None and len(lower[0]) !=0:
                output +="<sub>"+self.correct(self.translate(lower[0]))+"</sub>"
        return (output,i)


    def ddintegral(self,input,start):
        '''Translate triple integrals, including limits of integration.
        Returns touple.'''
        
        (lower,upper,i)=latex_access.get_subsuper(input,start)
        output =u" triple integral "
        
        # Statement to prevent the translator from empty boundaries:
        if lower is not None and upper is not None and len(lower[0]) !=0 and len(upper[0]) !=0:
            output +=" from "
            output +=self.correct(self.translate(lower[0]))
            output +=" to "
            output +=self.correct(self.translate(upper[0]))
            output +=" of "
        elif lower is not None and len(lower[0]) !=0:
                output +="<sub>"+self.correct(self.translate(lower[0]))+"</sub>"
        return (output,i)

    def ointegral(self,input,start):
        '''Translate double integrals, including limits of integration.
        Returns touple.'''
        
        (lower,upper,i)=latex_access.get_subsuper(input,start)
        output =u" loop integral "
        
        # Statement to prevent the translator from empty boundaries:
        if lower is not None and upper is not None and len(lower[0]) !=0 and len(upper[0]) !=0:
            output +=" from "
            output +=self.correct(self.translate(lower[0]))
            output +=" to "
            output +=self.correct(self.translate(upper[0]))
            output +=" of "
        elif lower is not None and len(lower[0]) !=0:
                output +="<sub>"+self.correct(self.translate(lower[0]))+"</sub>"
        return (output,i)

    def sum(self,input,start):
        '''Translate summas, including limits of summarization.
        Returns touple.'''
        
        (lower,upper,i)=latex_access.get_subsuper(input,start)
        output =u" sum "
        
        # Statement to prevent the translator from empty boundaries:
        if lower is not None and upper is not None and len(lower[0]) !=0 and len(upper[0]) !=0:
            output +=" where "
            output +=self.correct(self.translate(lower[0])).replace("equals"," goes from ")
            output +=" to "
            output +=self.correct(self.translate(upper[0]))
            output +=" of "
        elif lower is not None and len(lower[0]) !=0:
                output +="<sub>"+self.correct(self.translate(lower[0]))+"</sub>"
        return (output,i)

    def prod(self,input,start):
        '''Translate products, including limits of production.
        Returns touple.'''
        
        (lower,upper,i)=latex_access.get_subsuper(input,start)
        output =u" product "
        
        # Statement to prevent the translator from empty boundaries:
        if lower is not None and upper is not None and len(lower[0]) !=0 and len(upper[0]) !=0:
            output +=" where "
            output +=self.correct(self.translate(lower[0])).replace("equals"," goes from ")
            output +=" to "
            output +=self.correct(self.translate(upper[0]))
            output +=" of "
        elif lower is not None and len(lower[0]) !=0:
                output +="<sub>"+self.correct(self.translate(lower[0]))+"</sub>"
        return (output,i)

    def union(self,input,start):
        '''Translate unions, including limits of unition.
        Returns touple.'''
        
        (lower,upper,i)=latex_access.get_subsuper(input,start)
        output =u" union "
        
        # Statement to prevent the translator from empty boundaries:
        if lower is not None and upper is not None and len(lower[0]) !=0 and len(upper[0]) !=0:
            output +=" where "
            output +=self.correct(self.translate(lower[0])).replace("equals"," goes from ")
            output +=" to "
            output +=self.correct(self.translate(upper[0]))
            output +=" of "
        elif lower is not None and len(lower[0]) !=0:
                output +="<sub>"+self.correct(self.translate(lower[0]))+"</sub>"
        return (output,i)
    
    def cap(self,input,start):
        '''Translate intersections, including limits of intersection.
        Returns touple.'''
        (lower,upper,i)=latex_access.get_subsuper(input,start)
        output=u" intersection "
        # Statement to prevent the translator from empty boundaries:
        if lower is not None and upper is not None and len(lower[0]) !=0 and len(upper[0]) !=0:
            output +=" where "
            output +=self.correct(self.translate(lower[0])).replace(u"equals", u" goes from ")
            output +=u" to "
            output +=self.correct(self.translate(upper[0]))
            output+=u" of "
        elif lower is not None and len(lower[0]) !=0:
            output +="<sub>"+self.correct(self.translate(lower[0]))+"</sub>"
            
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

        If the log appears ambiguous, i.e. we can not reasonably
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
    
    def vect(self,input,start):
        arg=get_arg(input,start)
        if arg[0].isdigit() or len(arg[0])==1:
            translation=arg[0] +u" vector "
        else:
            translation =u" vector " +self.correct(self.translate(arg[0])) +u" end vector "
        return (translation,arg[1])

    def binom(self, input, start):
        '''Translate binomials into speech.
        Returns touple.'''
        
        arg_1=get_arg(input,start)
        if arg_1[1]<len(input):
            arg_2=get_arg(input,arg_1[1])
        else:
            arg_2=("",arg_1[1])
        
        if len(arg_1[0])==1 and len(arg_2[0])==1:
            translation =" %s choose %s " % (self.correct(self.translate(arg_1[0])), self.correct(self.translate(arg_2[0])))
        else:
            translation=u" begin binomial %s choose %s end binomial " % (self.correct(self.translate(arg_1[0])), self.correct(self.translate(arg_2[0])))
        return (translation, arg_2[1])

    def ln(self,input,start):
        '''Translate natural logs into speech.

        We translate natural logs in the form \ln(x) as
        loen of x. Usually natural logs do not have an extra base as day already to the base e by definition.

The natural log is correctly pronounced as loen and not as ln. 
        
        Returns a touple with translated string and index of
        first char after end of entire logarithm.'''

        ln=get_arg(input,start)
        translation=" loen "
        if len(ln[0]) < 1 or ln[0][0] != "_": # \ln by itself 
            return (translation, ln[2]) # ignore the supposed command 

        translation+="base "
        base=get_arg(input, ln[1])
        translation+=self.translate (base[0])
        translation+=" of "
        return (translation, base[1])
