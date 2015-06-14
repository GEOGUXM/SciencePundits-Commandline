import nltk


def nltk_major_version():
    return int(nltk.__version__.split('.')[0])
NLTK_VERSION = nltk_major_version()
    

def get_sentences(text):
    if text.strip() == '':
        return []
    tokens = nltk.sent_tokenize(text)
    sentences = []
    for sent in tokens:
        sentences.extend([s.strip() for s in sent.split('\n') if s.strip()])
    sentences_ = []
    skip_next = False
    for i, sent in enumerate(sentences):
        if skip_next:
            skip_next = False
            continue
        if i == len(sentences):
            sentences_.append(sent)
            break
        if sent.split()[-1].lower() == ('no.'):
            try:
                s1 = sentences[i+1]
                int(s1.split()[0])
                sentences_.append(sent + ' ' + s1)
                skip_next = True
            except ValueError:
                sentences_.append(sent)
        else:
            sentences_.append(sent)
    assert sentences[-1] in sentences_[-1]
    return sentences_


def pos_tag(tokens):
    return nltk.pos_tag(tokens)


def tokenize(text):
    text = text.replace('@', '__at__')
    tokens = nltk.word_tokenize(text)
    tokens = [t.replace('__at__', '@') for t in tokens]
    return tokens



_stemmer = None
def stem(word):
    global _stemmer
    if _stemmer is None:
        _stemmer = nltk.stem.porter.PorterStemmer()
    return _stemmer.stem_word(word)


_lemmatizer = None
def lemmatize(word):
    global _lemmatizer
    if _lemmatizer is None:
        _lemmatizer = nltk.WordNetLemmatizer()
    return _lemmatizer.lemmatize(word) 


def normalize(word):
    """Normalizes word to lowercase, stemmed, and lemmatized."""
    return lemmatize(stem(word.lower()))

