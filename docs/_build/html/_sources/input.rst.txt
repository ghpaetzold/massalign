.. highlightlang:: python

Input
=================

Here you will learn how to format your input for MASSAlign.

Documents
----------

MASSAlign's aligners take as input comparable documents separated at paragraph-level by empty lines. The documents must be in plain text format and pre-processed to your preference (tokenized, truecased, etc).

.. topic:: Here's an example:

	April is the fourth month of the year in the Gregorian Calendar , and one of four months with a length of 30 days .

	April was originally the second month of the Roman calendar , before January and February were added by King Numa Pompilius about 700 BC .
	It became the fourth month of the calendar year -LRB- the year when twelve months are displayed in order -RRB- during the time of the decemvirs about 450 BC , when it also was given 29 days .

	April starts on the same day of the week as July in all years , and January in leap years .
	April ends on the same day of the week as December every year .

	The birthstone of April is the diamond , and the birth flower is typically listed as either the Daisy or the Sweet Pea .
	April is commonly associated with the season of spring in the Northern hemisphere and autumn in the Southern hemisphere , where it is the seasonal equivalent to October in the Northern hemisphere and vice versa .
	
Word Alignments
----------------

One of the pieces of input taken by MASSAlign's annotators are word alignments, which have to be in Pharaoh format.

.. topic:: Here's an example:

	18-13 12-7 13-8 14-9 15-10 16-11 17-12 7-2 8-3 9-4 1-1 11-6
	
Constituency Parses
--------------------

MASSAlign's annotators also take as input constituency parses, which should be in its linear parenthesized form.

.. topic:: Here's an example:

	(ROOT (S (NP (NNP Hershey)) (VP (VBD left) (NP (DT no) (NNS heirs)) (SBAR (WHADVP (WRB when)) (S (NP (PRP he)) (VP (VBD died) (PP (IN in) (NP (CD 1945))) (, ,) (S (VP (VBG giving) (NP (NP (JJS most)) (PP (IN of) (NP (PRP$ his) (NN fortune)))) (PP (TO to) (NP (NN charity))))))))) (. .)))