from massalign.core import *
from massalign.util import *

#Get MASSA aligner for convenience:
m = MASSAligner()

#Create a sentence pair annotation example
reader = FileReader('https://ghpaetzold.github.io/massalign_data/annotator_data.txt')
data = reader.getRawText().split('\n')
src = data[0].strip()
ref = data[1].strip()
word_aligns = data[2].strip()
src_parse = data[3].strip()
ref_parse = data[4].strip()

#Annotate the pair:
annotator = SentenceAnnotator()
annotations = m.getSentenceAnnotations(src.split(' '), ref.split(' '), annotator, aligns=word_aligns, src_parse=src_parse, ref_parse=ref_parse)

#Display annotations:
m.visualizeSentenceAnnotations(src, ref, word_aligns, annotations)