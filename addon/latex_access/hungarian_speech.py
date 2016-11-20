# -*- coding: utf8 -*-
# speech.py
#	A part of the latex-access project at http://latex-access.sourceforge.net/
#	Author: Alastair Irving <alastair.irving@sjc.ox.ac.uk>
#	Modified by: Istvan Velegi <ivelegi@gmail.com>
#	Copyright (C) 2011 Alastair Irving/latex-access Contributors

#	This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation;
#	either version 2 of the License, or (at your option) any later version.
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#	See the GNU General Public License for more details.
#	You should have received a copy of the GNU General Public License along with this program; if not, visit <http://www.gnu.org/licenses>
#
'''Module to provide speech output for latex_access.'''

import latex_access
from latex_access import get_arg
import re

primes=re.compile(r"^\s*(\\p+rime\s*)+$")
argprimes=re.compile(r"^\s*\(.*\)$")
absertek =re.compile(r"\|([^\|]+)\|")
#norma =re.compile(r"\\|(.)\\|+")
sqrt_with_two_args =re.compile(r".*\\sqrt\[(.?)\]")

#Define a list of words to use as denominators of simple fractions
denominators=[" per 0 "," per 1 "," ketted"," harmad"," negyed",u" ötöd"," hatod"," heted"," nyolcad"," kilenced"]

class speech(latex_access.translator):
	'''Speech translator class.'''
	
	def __init__(self):
		self.handleBracketsAsPrime =False
		self.abbrev_first_root_arg =False
		latex_access.translator.__init__(self)
		self.files.append("speech.table")
		self.load_files()
		
		new_table={"\\cap":self.cap, "\\bigcap":self.cap, "\\binom":self.binom,"\\vec":self.vect,"\\underline":self.underline,"$":self.dollar,"^":self.super,"_":("<sub>","</sub>"),"\\pmod":("mod <sub>","</sub>"),"\\widetilde":self.tilde,"\\tilde":self.tilde,"\\sqrt":self.sqrt,"\\frac":self.frac,"\\dfrac":self.frac,"\\ds":self.dsfrac,"\\int":self.integral,"\\dbint":self.dbintegral,"\\ddint":self.ddintegral,"\\oint":self.ointegral,"\\cup":self.union,"\\bigcup":self.union,"\\sum":self.sum,"\\prod":self.prod,"\\bf":("<bold>","</bold>"),"\\mathbf":("<bold>","</bold>"),"\\mathbb":("<bold>","</bold>"),"\\mathcal":("<mathcal>","</mathcal>"), "\\em":("<em>","</em>"), "\\it":("<em>","</em>"), "\\log":self.log,"\\ang":self.ang,"\\tag":self.tag,"\\hat":self.hat,"\\widehat":self.hat,"\\bar":("",u" felülvonás "),"\\overline":self.overline,"\\dot":("","pont"),"\\ddot":("","duplapont")}
		for (k,v) in new_table.iteritems():
			self.table[k]=v
			self.space=" "


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
	
	def lowerSuffixParse(self, inputstr):
		l1 =["1", "2", "4", "5", "7", "9", "x", "b", "c"]
		l2 =["3", "6", "8", "y"]
		if len(inputstr) ==0:
			return u"-tól "
		if len(inputstr) >1 and inputstr.endswith(u"egyenlő 0") or inputstr[:-1].isdigit() and inputstr[-2] ==u"0" and inputstr[-1] ==u"0" and inputstr !=u"1000":
			return inputstr+u"-tól "
		if inputstr ==u"0":
			return u" nullától "
		if inputstr[-1].lower() in l1:
			return inputstr+u"-től "
		elif inputstr[-1].lower() in l2:
			return inputstr +u"-tól "
		else:
			if inputstr[-1].lower() ==u"a":
				return inputstr[:-1] +inputstr[-1].lower().replace(u"a", u"ától ")
			if inputstr[-2:].lower() =="a ":
				return inputstr[:-2] +inputstr[-2:].lower().replace(u"a ", u"ától ")
			return inputstr +u"-től "

	def upperSuffixParse(self, inputstr):
		if inputstr.lower().endswith("a"):
			return inputstr[:-1] +inputstr[-1].lower().replace(u"a", u"áig ")
		elif inputstr[-2:] =="a ":
			return inputstr[:-2] +inputstr[-2:].lower().replace(u"a ", u"áig ")
		else:
			return inputstr +u"-ig "

	def super(self,input,start):
		'''Translate  superscripts into speech.
		Returns a touple with translated string and index of
		first char after end of super.'''
		
		arg_with_minus =re.compile(r"-.?")
		arg=get_arg(input,start)
		#Handle squared and cubed as special cases
		if arg[0] == "2":
			translation=u" négyzet "
		elif arg[0]=="3":
			translation=u" köb "
			
		elif len(arg[0]) <2 or arg_with_minus.match(arg[0]):
			translation =u" ad %s, " % self.correct(self.translate(arg[0]))
			
		#Handle primes
		elif primes.match(arg[0]):
			if arg[0].count("p") ==1:
				if arg[0].count("\\prime") ==1:
					translation=u" vessző "
				else:
					translation=u" " +str(arg[0].count("\\prime")).replace("2", u"két") +u" vessző "
			elif arg[0].count("p") >1:
				translation=u" " +str(self.correct(arg[0]).count("p")).replace("2", u"két") +u" vessző "
				
		elif argprimes.match(arg[0]) and self.handleBracketsAsPrime:
			translation =u" %s " % self.translate(self.correct(arg[0])) +u" vessző "
		else:
			translation = u" ad <sup> %s </sup>" % self.translate(self.correct(arg[0]))
		return (translation, arg[1])

	def sqrt(self,input,start):
		'''Translates roots into speech.

		returns touple.'''
		if sqrt_with_two_args.match(input):
			first_arg =latex_access.get_optional_arg(input, start)
			second_arg=get_arg(input, first_arg[1])
			
			if self.abbrev_first_root_arg ==True:
				if first_arg[0].isdigit() or len(first_arg[0]) ==1:
					translation =denominators[int(first_arg[0])] +" "
				elif first_arg[0] in ["x", "n"] and len(first_arg[0]) ==1:
					translation =first_arg[0] +u"-ed "
				elif first_arg[0] =="3":
					translation =u" köb "
				else:
					translation =self.correct(self.translate(first_arg[0])) +u". "

			else:
				if first_arg[0] =="3":
					translation =u" köb "
				elif first_arg[0].lower() =="n":
					translation =u"n-edik "
				elif first_arg[0] =="x":
					translation ="x-edik "
				else:
					translation =self.correct(self.translate(first_arg[0])) +u". "
					
			if len(second_arg[0]) ==1:
				translation +=u" gyök " +self.correct(self.translate(second_arg[0]))
			else:
				translation +=u" gyök alatt, "+self.correct(self.translate(second_arg[0])) +u", gyök zár "
			return (translation, second_arg[1])
		
		arg=get_arg(input, start)
		if arg[0].isdigit() or len(arg[0])==1:
			translation=u" gyök " +arg[0]
		else:
			translation=u" gyök alatt, " +self.correct(self.translate(arg[0])) +u", gyök zár"
		return (translation,arg[1])

	def norma(self, input, start):
		m =absertek.match(input)

		if m is not None:
			arg=get_arg("{"+m.group(1)+"}", 0)
			if len(arg[0]) ==1:
				output =self.translate(arg[0])+u" abszolút "
				return (output, arg[1])
			else:
				output =u" abszolút " +self.translate(arg[0]+u" abszolút ")
				return (output, arg[1])
		else:
			arg =get_arg(input, start-1)
			output =u" függőleges "
			return (output, arg[1])


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
					translation+=""
				translation+=" "
			else:
				translation =" %s per %s " % (self.correct(numerator[0]), self.correct(denominator[0]))
		else:
			translation=u" tört, %s per %s, tört zár " % (self.translate(self.correct(numerator[0])), self.translate(self.correct(denominator[0])))
		return (translation,denominator[1])

	def dsfrac(self,input,start):
		arg=get_arg(input,start)
		translation=u" tört "+self.correct(self.translate(arg[0])) +u" tört zár "
		return (translation,arg[1])

	def integral(self,input,start):
		'''Translate integrals, including limits of integration.
		Returns touple.'''
		
		(lower,upper,i)=latex_access.get_subsuper(input,start)
		output =u"integrál "
		if lower is not None and upper is not None and len(lower[0]) !=0 and len(upper[0]) !=0:
			output +=self.lowerSuffixParse(self.translate(lower[0]))
			output +=self.upperSuffixParse(self.translate(upper[0]))
		else:
			if lower is not None and len(lower[0]) !=0:
				output +="<sub>"+self.correct(self.translate(lower[0]))+"</sub>"
		return (output,i)

	def dbintegral(self,input,start):
		'''Translate integrals, including limits of integration.
		Returns touple.'''
		output =u"kettős integrál "
		(lower,upper,i)=latex_access.get_subsuper(input,start)
		if lower is not None and upper is not None and len(lower[0]) !=0 and len(upper[0]) !=0:
			output +=self.lowerSuffixParse(self.translate(lower[0]))
			output +=self.upperSuffixParse(self.translate(upper[0]))
		else:
			if lower is not None and len(lower[0]) !=0:
				output +="<sub>"+self.correct(self.translate(lower[0]))+"</sub>"
		return (output,i)

	def ddintegral(self,input,start):
		'''Translate integrals, including limits of integration.
		Returns touple.'''
		
		(lower,upper,i)=latex_access.get_subsuper(input,start)
		output =u"hármas integrál "
		if lower is not None and upper is not None and len(lower[0]) !=0 and len(upper[0]) !=0:
			output +=self.lowerSuffixParse(self.translate(lower[0]))
			output +=self.upperSuffixParse(self.translate(upper[0]))
		else:
			if lower is not None and len(lower[0]) !=0:
				output +="<sub>"+self.correct(self.translate(lower[0]))+"</sub>"
		return (output,i)
	
	def ointegral(self,input,start):
		'''Translate integrals, including limits of integration.
		Returns touple.'''
		
		(lower,upper,i)=latex_access.get_subsuper(input,start)
		output =u"hurokintegrál "
		if lower is not None and upper is not None and len(lower[0]) !=0 and len(upper[0]) !=0:
			output +=self.lowerSuffixParse(self.translate(lower[0]))
			output +=self.upperSuffixParse(self.translate(upper[0]))
		elif lower is not None and len(lower[0]) !=0:
			output +="<sub>"+self.correct(self.translate(lower[0]))+"</sub>"
			
		return (output,i)

	def sum(self,input,start):
		'''Translate summas, including limits of summarization.
		Returns touple.'''
		input.replace("\\limits", "")
		(lower,upper,i)=latex_access.get_subsuper(input,start)
		output=u" szumma "
		if lower is not None and upper is not None and len(lower[0]) !=0 and len(upper[0]) !=0:
			output +=self.lowerSuffixParse(self.translate(lower[0])).replace(u"egyenlő", u"megy")
			output +=self.upperSuffixParse(self.translate(upper[0]))
		elif lower is not None and len(lower[0]) !=0:
			output +="<sub>"+self.correct(self.translate(lower[0]))+"</sub>"
			
		return (output,i)

	def prod(self,input,start):
		'''Translate products, including limits of producttion.
		Returns touple.'''
		input.replace("\\limits", "")
		(lower,upper,i)=latex_access.get_subsuper(input,start)
		output=u" produktum "
		if lower is not None and upper is not None and len(lower[0]) !=0 and len(upper[0]) !=0:
			output +=self.lowerSuffixParse(self.translate(lower[0])).replace(u"egyenlő", u"megy")
			output +=self.upperSuffixParse(self.translate(upper[0]))
		elif lower is not None and len(lower[0]) !=0:
			output +="<sub>"+self.correct(self.translate(lower[0]))+"</sub>"
			
		return (output,i)

	def union(self,input,start):
		'''Translate unions, including limits of unition.
		Returns touple.'''
		(lower,upper,i)=latex_access.get_subsuper(input,start)
		output=u" unió "
		if lower is not None and upper is not None and len(lower[0]) !=0 and len(upper[0]) !=0:
			output +=self.lowerSuffixParse(self.translate(lower[0])).replace(u"egyenlő", u"megy")
			output +=self.upperSuffixParse(self.translate(upper[0]))
		elif lower is not None and len(lower[0]) !=0:
			output +="<sub>"+self.correct(self.translate(lower[0]))+"</sub>"
			
		return (output,i)

	def cap(self,input,start):
		'''Translate intersections, including limits of intersection.
		Returns touple.'''
		(lower,upper,i)=latex_access.get_subsuper(input,start)
		output=u" metszet "
		if lower is not None and upper is not None and len(lower[0]) !=0 and len(upper[0]) !=0:
			output +=self.lowerSuffixParse(self.translate(lower[0])).replace(u"egyenlő", u"megy")
			output +=self.upperSuffixParse(self.translate(upper[0]))
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
		if len(log[0]) < 1 or log[0][0] != "_": # \log by itself 
			return (" log ", log[2]) # ignore the supposed command 

		# Safe to assume log is of the form \log_a(x)
		translation =u""
		base=get_arg(input, log[1])
		translation+=self.translate(base[0])
		translation+=u" alapú logaritmus "
		
		return (translation, base[1])

	def underline(self,input,start):
		arg=get_arg(input,start)
		translation=self.translate(arg[0])
		return (translation,arg[1])

	def overline(self,input,start):
		arg=get_arg(input,start)
		if arg[0].isdigit() or len(arg[0])==1:
			translation=arg[0]+u" felülvonás "
		else:
			translation=u" felülvonás "+self.translate(self.correct(arg[0])) +u" felülvonás zár "
		return (translation,arg[1])

	def tilde(self,input,start):
		arg=get_arg(input,start)
		if arg[0].isdigit() or len(arg[0])==1:
			translation=arg[0]+u" hullám "
		else:
			translation=u" hullám "+self.translate(self.correct(arg[0])) +u" hullám zár "
		return (translation,arg[1])

	def hat(self,input,start):
		arg=get_arg(input,start)
		if arg[0].isdigit() or len(arg[0])==1:
			translation=arg[0]+u" kalap "
		else:
			translation=u" kalap "+self.translate(self.correct(arg[0])) +u" kalap zár "
		return (translation,arg[1])

	def vect(self,input,start):
		arg=get_arg(input,start)
		if arg[0].isdigit() or len(arg[0])==1:
			translation=arg[0].replace("a", u"á") +u" vektor "
		else:
			translation=u" vektor, "+self.translate(self.correct(arg[0])) +u", vektor zár "
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
			translation =" %s alatt %s " % (self.correct(self.translate(arg_1[0])), self.correct(self.translate(arg_2[0])))
		else:
			translation=u" binom, %s alatt %s, binom zár " % (self.correct(self.translate(arg_1[0])), self.correct(self.translate(arg_2[0])))
		return (translation, arg_2[1])
	
