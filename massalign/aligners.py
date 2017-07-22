from abc import ABCMeta, abstractmethod

class ParagraphAligner:

    __metaclass__ = ABCMeta

    @abstractmethod
    def alignParagraphs(self):
        pass
		
class VicinityDrivenParagraphAligner(ParagraphAligner):

	def __init__(self):
		pass
		
	def alignParagraphs(self, p1=[], p2=[]):
		pass