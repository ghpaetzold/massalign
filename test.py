from massalign.core import *
from massalign.aligners import *

file = '../newsela/corpora/truecased_corpus/orioles-alvarez.en.0.txt'

m = MASSAligner()
data = m.getParagraphsFromDocument(file)
print data