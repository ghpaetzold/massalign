from operator import itemgetter
from nltk.tree import ParentedTree

# =============================================================================
# Constants
# =============================================================================


CLAUSE_SYNT_TAGS = ['SBAR', 'CC']

CHUNK_SYNT_TAGS = ['NP', 'VP', 'PP']

REWRITE_LIST = ['that', 'what', 'which', 'who', 'whom', 'a', 'an', 'the', 'of', 'at', 'by', 'into', 'in', 's', "'s",
                't', "'t", 'can', 'don', 'should', 'd', 'll', 'm', 're', 've', 'ain', 'aren', 'couldn', 'didn', 'doesn',
                'hadn', 'hasn', 'haven', 'isn', 'mustn', 'needn', 'shan', 'shouldn', 'wasn', 'weren', 'won', 'wouldn']

SIMOP_LABELS_GROUPS = dict(add=['B-A', 'B-AC', 'I-A', 'I-AC'], delete=['B-D', 'B-DC', 'I-D', 'I-DC'],
                           replace=['B-R', 'I-R'], move=['B-M', 'B-MC', 'I-M', 'I-MC'],
                           replacemove=['B-RM', 'I-RM'], rewrite=['B-RW', 'I-RW'], rewritemove=['B-RWM', 'I-RWM'])

SIMOP_LABELS = ['B-A', 'B-AC', 'B-D', 'B-DC', 'B-M', 'B-MC', 'B-R', 'B-RM', 'B-RW', 'B-RWM',
                'I-A', 'I-AC', 'I-D', 'I-DC', 'I-M', 'I-MC', 'I-R', 'I-RM', 'I-RW', 'I-RWM']


class SentenceAnnotator:
    """
    Implements algorithms for annotating transformation operations between parallel sentences.
    """

    def __init__(self):
        self.name = "Sentence Annotator"

    # =============================================================================
    # Main Annotation Functions
    # =============================================================================

    def getSentenceAnnotations(self, src, ref, aligns, src_parse, ref_parse):
        """
        Annotates the transformation operations between a pair of aligned sentences (source and reference).

        * *Parameters*:
            * **src**: A list of words corresponding to the tokenized source sentence.
            * **ref**: A list of words corresponding to the tokenized reference sentence.
            * **aligns**: A string containing the word alignments between source and reference, in Pharaoh format.
            * **src_parse**: A string containing the constituent parse tree of the source sentence.
            * **ref_parse**: A string containing the constituent parse tree of the reference sentence.
        * *Output*:
            * **sent_annots**: A dictionary containing the token-level annotations for both source and reference sentences.
        """

        if isinstance(aligns, str) or isinstance(aligns, unicode):
            aligns = self._formatWordAlignments(aligns)

        # token-level delete, add and replace
        src_annots = self._labelDeleteReplace(src, ref, aligns)
        ref_annots = self._labelAddReplace(ref, aligns, src_annots)

        # simple heuristic to improve token-level replacements
        self._improveReplace(src_annots, ref_annots, src_parse, ref_parse)

        # token-level rewrite
        self._labelRewrite(src_annots, ref_annots)

        # token-level move
        self._labelMove(src_annots, ref_annots, aligns)

        # clause-level delete and add
        self._labelGroupSimop(src_annots, src_parse, CLAUSE_SYNT_TAGS, ['B-D', 'I-D'], 'DC')
        self._labelGroupSimop(ref_annots, ref_parse, CLAUSE_SYNT_TAGS, ['B-A', 'I-A'], 'AC')

        # chunk-level delete and add
        self._labelGroupSimop(src_annots, src_parse, CHUNK_SYNT_TAGS, ['B-D', 'I-D'], 'D', majority_percent=1)
        self._labelGroupSimop(ref_annots, ref_parse, CHUNK_SYNT_TAGS, ['B-A', 'I-A'], 'A', majority_percent=1)

        # clause-level move
        self._labelGroupSimop(src_annots, src_parse, CLAUSE_SYNT_TAGS, ['B-M', 'I-M'], 'MC')

        # chunk-level move
        self._labelGroupSimop(src_annots, src_parse, CHUNK_SYNT_TAGS, ['B-M', 'I-M'], 'M', majority_percent=1)

        # adding 'destination' for some B- 'move'tokens in clause and chunk levels
        self._correct_move(src_annots)

        sent_annots = dict(src=src_annots, ref=ref_annots)

        # return the transformations annotations for the parallel sentences
        return sent_annots

    def getSentenceAnnotationsForFile(self, sents_file, aligns_file, parse_file, verbose=True):
        """
        Annotates all the parallel sentences in a given file. Each sentence pair appears in a separate line.

        * *Parameters*:
            * **sents_file**: File containing the parallel sentences. Each line in the file contains a source-reference pair, separated by the character |||.
            * **aligns_file**: File containing the word alignments between each sentence pair. Each line contains the alignments in Pharaoh format.
            * **parse_file**: File containing the parse trees of the parallel sentences. Every two lines in the file corresponds to a sentence pair (the first is the source parse and the second the reference parse).
            * **verbose**: Indicates whether to print a message indicating the sentence being annotated or not.
        * *Output*:
            * **file_annots**: A list of dictionaries, each of them containing the sentence pair id and the annotations for the corresponding source and reference sentences.
        """

        file_annots = []
        sent_id = 0
        for sents_pair, aligns_pairs in zip(sents_file, aligns_file):
            sent_id += 1
            if verbose:
                print("Annotating sentence", sent_id, '.')

            # get the aligned sentences and format them
            src_sent, ref_sent = sents_pair.split('|||')
            src = src_sent.strip().split(' ')
            ref = ref_sent.strip().split(' ')

            # get the word alignments pairs
            aligns_list = self._formatWordAlignments(aligns_pairs)

            # get the parsed sentences
            src_parse = parse_file.readline()
            ref_parse = parse_file.readline()

            # annotate the simplification operations
            sent_annots = self.getSentenceAnnotations(src, ref, aligns_list, src_parse, ref_parse)

            sent_annots['id'] = sent_id

            file_annots.append(sent_annots)

        # return the transformations annotations for all the parallel sentences in the file
        return file_annots

    # =============================================================================
    # Output Functions
    # =============================================================================

    def createConllFiles(self, annot_file_src, annot_file_ref, annotations, include_clauseop=True, labels_to_print=SIMOP_LABELS):
        """
        Creates files in conll format for the transformation annotations of given parallel sentences.

        * *Parameters*:
            * **annot_file_src**: The file where to write the annotations for the source sentence.
            * **annot_file_ref**: The file where to write the annotations for the reference sentence.
            * **annotations**: A list of dictionaries containing the annotations for the corresponding source and reference sentences.
            * **include_clauseop**: Indicates whether to print labels corresponding to clause-level operations.
            * **labels_to_print**: Which transformation operation labels to print. By default, all are printed.
        """

        conll_src = ""
        conll_ref = ""
        for sent in annotations:
            # create the information for one sentence of the file considering the filters given as parameters
            conll_src += self._dict2conll(sent['src'], include_clauseop, labels_to_print, 'C') + '\n'
            conll_ref += self._dict2conll(sent['ref'], include_clauseop, labels_to_print, 'O') + '\n'

        # write the annotations in the source and reference files
        annot_file_src.write(conll_src)
        annot_file_ref.write(conll_ref)

    def _dict2conll(self, sent_annots, include_clauseop=True, labels_to_print=SIMOP_LABELS, default_label='C'):
        """
        Formats the transformation annotations of a sentence into conll format.

        * *Parameters*:
            * **sent_annots**: A dictionary containing the transformation operations in a sentence.
            * **include_clauseop**: Indicates whether to print labels corresponding to clause-level operations.
            * **labels_to_print**: Which transformation operation labels to print. By default all are printed.
            * **default_label**: Label to use for tokens that do not have a particular transformation operation.
        * *Output*:
            * **conll**: A string containing the sentence transformations annotations in conll format
        """

        conll = ""
        for token in sent_annots:
            label = token['label']
            if label in labels_to_print:
                if not include_clauseop:
                    if label in ['B-AC', 'I-AC', 'B-DC', 'I-DC', 'B-MC', 'I-MC']:
                        label = label[0:3]  # remove the 'C' indicating the clause-level correspondance
                if label in ['B-R', 'B-RW']:
                    label += '\t' + ' '.join(token['replace'])  # add the gold replacement token
                if label in ['B-M', 'B-MC', 'B-RM', 'B-RWM']:
                    label += '\t' + str(token['move'])  # add the gold position to be moved
            else:
                label = default_label
            # form the line of information corresponding to the current token
            conll += str(token['index']) + '\t' + token['word'] + '\t' + label + '\n'

        # return the annotations in conll format for the whole sentence
        return conll

    # =============================================================================
    # Internal Annotation Functions
    # =============================================================================

    def _formatWordAlignments(self, aligns):
        """
        Transforms the word alignments given as a string into a list of 2-element lists.

        * *Parameters*:
            * **aligns**: A string containing the word alignments between source and reference, in Pharaoh format.
        * *Output*:
            * **aligns_list**: A list of list containing the word alignments
        """

        aligns_list = []
        if aligns.strip() != '':
            aligns = aligns.strip().split(' ')
            # transform them into a list of lists: ['1-1', '2-2', '3-4'] -> [[1, 1], [2, 2], [3, 4]]
            aligns_list = [list(map(int, p.split('-'))) for p in aligns]

        # return the alignments as a list of 2-element lists
        return aligns_list

    def _labelDeleteReplace(self, src, ref, aligns):
        """
        Annotates deletions and replacements in the source sentence.

        * *Parameters*:
            * **src**: A list of words corresponding to the tokenized source sentence.
            * **ref**: A list of words corresponding to the tokenized reference sentence.
            * **aligns**: A list of 2-element lists containing the word alignments between source and reference.
        * *Output*:
            * **src_annots**: A dictionary containing token-level annotations for deletions and replacements in the source sentence.
        """

        src_annots = []
        for token_index, token_word in enumerate(src, start=1):
            src_token = {'index': token_index, 'word': token_word, 'label': ''}
            # get the indexes of all the words in the reference to which the current token in source is aligned to
            aligns_list = [ref_index for src_index, ref_index in aligns if src_index == token_index]
            # check if the token is aligned
            if aligns_list:
                # check if it has been aligned to only one token and if they are exactly the same
                if len(aligns_list) == 1 and token_word.lower() == ref[aligns_list[0] - 1].lower():
                    # it is a 'keep'
                    src_token['label'] = 'O'
                else:
                    # it is a 'replacement'
                    src_token['label'] = 'B-R'
                    src_token['replace'] = []
                    # recover all the tokens in reference for which this token in source is replaced
                    aligns_list.sort()
                    for ref_index in aligns_list:
                        src_token['replace'].append(ref[ref_index - 1])
            else:
                # label as delete
                src_token['label'] = 'B-D'

            src_annots.append(src_token)

        src_annots = sorted(src_annots, key=itemgetter('index'))

        return src_annots

    def _labelAddReplace(self, ref, aligns, src_annots):
        """
        Annotates additions in the reference sentence. Also, adds multi-word replacements in the source sentence.

        * *Parameters*:
            * **ref**: A list of words corresponding to the tokenized reference sentence.
            * **aligns**: A list of 2-element lists containing the word alignments between source and reference.
            * **src_annots**: A dictionary containing token-level annotations in the source sentence.
        * *Output*:
            * **ref_annots**: A dictionary containing token-level annotations for additions in the reference sentence.
        """

        ref_annots = []
        for token_index, token_word in enumerate(ref, start=1):
            ref_token = {'index': token_index, 'word': token_word, 'label': ''}
            # get the indexes of all the tokens in the source to which the current token in reference is aligned
            aligns_list = [src_index for src_index, ref_index in aligns if ref_index == token_index]
            # check if the token is aligned
            if aligns_list:
                # it is the replacement of some word(s) in the source
                ref_token['label'] = 'O'  # the token in the reference has no label
                if len(aligns_list) > 1:
                    # it is the replacement of a phrase in source, so the source token annots_file should be changed
                    aligns_list.sort()
                    for i in range(1, len(aligns_list)):  # token 0 already has 'B-R' because of label_delete_replace
                        src_index = aligns_list[i]
                        src_token = [src_token for src_token in src_annots if src_token['index'] == src_index][0]
                        src_token['label'] = 'I-R'
                        src_token['replace'] = []  # token with 'B-R' has all the replacement tokens
            else:
                # label as 'add'
                ref_token['label'] = 'B-A'

            ref_annots.append(ref_token)

        ref_annots = sorted(ref_annots, key=itemgetter('index'))

        return ref_annots

    def _improveReplace(self, src_annots, ref_annots, src_parse, ref_parse):
        """
        Applies a simple heuristic based on transformation operations labels, sentence positions and part-of-speech tags
        to improve the annotation of replacements.

        * *Parameters*:
            * **src_annots**: A dictionary containing token-level annotations in the source sentence.
            * **ref_annots**: A dictionary containing token-level annotations in the reference sentence.
            * **src_parse**: A string containing the constituent parse tree of the source sentence.
            * **ref_parse**: A string containing the constituent parse tree of the reference sentence.
        """

        for ref_token in ref_annots:
            # check that the token has been labeled as 'add'
            if ref_token['label'] == 'B-A':
                # find a token in source, with the same index and labeled as 'delete'
                same_index_in_src = [src_token for src_token in src_annots if
                                     src_token['index'] == ref_token['index'] and src_token['label'] == 'B-D']
                if same_index_in_src:  # it is not an empty list
                    src_token = same_index_in_src[0] # there is always one at the most
                    # check that both tokens have the same part of speech tag
                    same_postag = self._have_same_postag(src_token['index'], ref_token['index'], src_parse, ref_parse)
                    if same_postag:
                        src_token['label'] = 'B-R'  # the token in the source must be labeled as replace
                        ref_token['label'] = 'O'  # the token in the reference now has no label
                        src_token['replace'] = [ref_token['word']]  # include the information of the replacement

    def _labelRewrite(self, src_annots, ref_annots):
        """
        Annotate rewrites as particular cases of 'replace' (in source) and 'add' (in reference).

        * *Parameters*:
            * **src_annots**: A dictionary containing token-level annotations in the source sentence.
            * **ref_annots**: A dictionary containing token-level annotations in the reference sentence.
        """

        # find replacements which belong to the rewrite list
        for src_token in src_annots:
            if src_token['label'] == 'B-R' and src_token['word'].lower() in REWRITE_LIST:
                src_token['label'] = 'B-RW'

        # find isolated adds which belong to the rewrite list
        for ref_token in ref_annots:
            if ref_token['label'] == 'B-A' and ref_token['word'].lower() in REWRITE_LIST:
                # check if the token before is an 'add'
                if ref_token['index'] > 1:
                    # the tokens in the sentence are 1-indexed, but their position in the array is 0-indexed
                    add_before = ref_annots[ref_token['index']-2]['label'] in ['B-A', 'I-A', 'I-AC']
                else:
                    add_before = False

                # check if the token after is an 'add'
                if ref_token['index'] < len(ref_annots):
                    # the tokens in the sentence are 1-indexed, but their position in the array is 0-indexed
                    add_after = ref_annots[ref_token['index']]['label'] in ['B-A', 'I-A', 'B-AC']
                else:
                    add_after = False

                # check if it is an isolated 'add'
                if not add_before and not add_after:
                    ref_token['label'] = 'B-RW'
                    ref_token['replace'] = [ref_token['word']]

    def _labelMove(self, src_annots, ref_annots, aligns):
        """
        Annotate 'move' checking if the relative index of a token in source changes in reference, considering
        preceding deletions, additions and multi-token replacements.

        * *Parameters*:
            * **src_annots**: A dictionary containing token-level annotations in the source sentence.
            * **ref_annots**: A dictionary containing token-level annotations in the reference sentence.
            * **aligns**: A list of 2-element lists containing the word alignments between source and reference.
        """

        shift_left = 0
        for src_token in src_annots:
            # check if the token has been labeled to be deleted or as part of a replace or rewrite
            if src_token['label'] in ['B-D', 'B-DC', 'I-DC', 'I-D', 'I-R', 'I-RW']:
                shift_left += 1
            else:
                # get its position in the reference (using the word alignments)
                ref_index_list = [ref_index for src_index, ref_index in aligns if src_index == src_token['index']]
                if ref_index_list:
                    ref_index = ref_index_list[0]
                else:
                    ref_index = src_token['index']

                # count the number 'add' and 'rewrite' to the reference up until the new position of the source token
                shift_right = 0
                for ref_token in ref_annots:
                    if ref_token['index'] < ref_index:
                        if ref_token['label'] in ['B-A', 'B-AC', 'I-AC', 'I-A', 'B-RW']:
                            shift_right += 1
                    else:
                        break

                # check if the token needs to be moved
                if (src_token['index'] - shift_left + shift_right) != ref_index:
                    if src_token['label'] == 'O':  # the token is kept and moved
                        new_label = 'B-M'
                    elif src_token['label'] == 'B-R':  # the token is replaced and moved
                        new_label = 'B-RM'
                    elif src_token['label'] == 'B-RW':  # the token is rewritten and moved
                        new_label = 'B-RWM'
                    else:
                        new_label = src_token['label']  # in any other case, the label stays the same
                    src_token['label'] = new_label
                    src_token['move'] = ref_index

    def _labelGroupSimop(self, annots, parse, group_synt_tags, old_token_labels, new_group_label, majority_percent=0.75):
        """
        Annotates a sequence of tokens with the same operation label and that belong to the same syntactic group,
        with a given group operation label.

        * *Parameters*:
            * **annots**: A dictionary containing token-level annotations for the sentence.
            * **parse**: A string containing the constituent parse tree of the sentence.
            * **group_synt_tags**: A list of the syntactic labels that identify a group.
            * **old_token_labels**: A list of transformation operation labels to the replaced by new ones.
            * **new_group_label**: A list of transformation operation labels that will be the replacements of the old ones.
            * **majority_percent**: The minimum percentage of tokens in the syntactic group that must have the same old_token_labels for the whole syntactic group to change to the new labels.
        """
        parse_tree = ParentedTree.fromstring(parse)
        num_tokens = len(annots)

        for ptr_token in range(0, num_tokens):
            token = annots[ptr_token]
            if token['label'] in old_token_labels:
                # get the subtree of the token
                treepos = parse_tree.leaf_treeposition(token['index'] - 1)
                subtree = parse_tree[treepos[:-1]]

                # find if it belongs to the specified syntactic group
                parent = subtree.parent()
                while parent and parent.label() not in group_synt_tags:
                    parent = parent.parent()

                if parent:  # the token is inside one of the specified syntactic groups
                    # get the index of the first token in the group, according to the parse tree
                    begin = parse_tree.treepositions('leaves').index(parent.treeposition() + parent.leaf_treeposition(0))

                    # count the number of tokens in the group that have been labeled with the same operation
                    with_same_label = 0
                    group_tokens = parent.leaves()
                    for gt in group_tokens:
                        if gt == token['word']:  # check if the word in the group has been labeled
                            if token['label'] in old_token_labels:
                                with_same_label += 1
                            ptr_token += 1
                            if ptr_token == num_tokens:  # check that there are still tokens annotated
                                break
                            token = annots[ptr_token]

                    # check if the majority of the tokens in the group have been labeled with the same operation
                    if with_same_label >= majority_percent * len(group_tokens):
                        end = begin + with_same_label

                        # label the first token in the group
                        token = annots[begin]
                        token['label'] = 'B-' + new_group_label
                        group_begin = token['index']
                        token['groupbegin'] = group_begin

                        # label the rest of the tokens in the group
                        for i in range(begin + 1, end):
                            token = annots[i]
                            token['label'] = 'I-' + new_group_label
                            token['groupbegin'] = group_begin
                        ptr_token -= 1
                    else:
                        ptr_token = begin

    def _correct_move(self, src_annots):
        """
        Add missing destination information for some automatically annotated 'move' tokens.

        * *Parameters*:
            * **annots**: A dictionary containing token-level annotations for the source sentence.
        """

        looking = False
        for token_ptr, token in enumerate(src_annots):
                # determine if the token is at the beginning or inside a 'move' sequence
                if ('B-' in token['label']) and ('move' not in token.keys()):
                    looking = True  # we need to look for the position to which this sequence need to be moved
                    begin_ptr = token_ptr  # for easier access once we find the information we need
                elif ('I-' in token['label']) and ('move' in token.keys()) and looking:
                    looking = False  # we found a token inside the sequence which has the information we need
                    src_annots[begin_ptr]['move'] = token['move'] - (token_ptr - begin_ptr)

    def _have_same_postag(self, src_index, ref_index, src_parse, ref_parse):
        """
        Check if two tokens in two parse trees have the same part-of-speech tag, given their indexes.

        * *Parameters*:
            * **src_index**: The index of the token to compare in the source sentence.
            * **ref_index**: The index of the token to compare in the reference sentence.
            * **src_parse**: A string containing the constituent parse tree of the source sentence.
            * **ref_parse**: A string containing the constituent parse tree of the reference sentence.
        * *Output*:
            * **same_postag**: Indicates whether the two tokens have the same part-of-speech tag or not.
        """

        # get the parse trees from the string format
        src_tree = ParentedTree.fromstring(src_parse)
        ref_tree = ParentedTree.fromstring(ref_parse)

        # get the part-of-speech tag of the token in the source sentence
        src_treepos = src_tree.leaf_treeposition(src_index - 1)
        src_subtree = src_tree[src_treepos[:-1]]
        src_postag = src_subtree.label()

        # get the part-of-speech tag of the token in the reference sentence
        ref_treepos = ref_tree.leaf_treeposition(ref_index - 1)
        ref_subtree = ref_tree[ref_treepos[:-1]]
        ref_postag = ref_subtree.label()

        # return whether the two tokens have the same part-of-speech tag or not
        return src_postag == ref_postag
