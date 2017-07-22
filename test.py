from massalign.core import *

file1 = '../newsela/corpora/truecased_corpus/orioles-alvarez.en.0.txt'
file2 = '../newsela/corpora/truecased_corpus/orioles-alvarez.en.1.txt'

m = MASSAligner()
p1s = m.getParagraphsFromDocument(file1)
p2s = m.getParagraphsFromDocument(file2)

aligner = VicinityDrivenParagraphAligner()

alignments = m.getParagraphAlignments(p1s, p2s, aligner) 