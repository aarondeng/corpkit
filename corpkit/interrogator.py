"""
corpkit: Interrogate a parsed corpus
"""

from __future__ import print_function
from corpkit.constants import STRINGTYPE, PYTHON_VERSION, INPUTFUNC


def welcome_printer(search, cname, optiontext, return_it=False, printstatus=True):
    """Print welcome message"""
    from time import localtime, strftime
    if printstatus:
        thetime = strftime("%H:%M:%S", localtime())
        from corpkit.process import dictformat
        sformat = dictformat(search)
        welcome = ('\n%s: Interrogating %s ...\n          %s\n          ' \
                    'Query: %s\n          Interrogating corpus ... \n' % \
                  (thetime, cname, optiontext, sformat))
        if return_it:
            return welcome
        else:
            print(welcome)

def fix_show_bit(show_bit):
    """
    Take a single search/show_bit type, return match
    """
    ends = ['w', 'l', 'i', 'n', 'f', 'p', 'x', 's', 'a', 'e', 'c']
    starts = ['d', 'g', 'm', 'b', 'h', '+', '-', 'r', 'c']
    show_bit = show_bit.lstrip('n')
    show_bit = show_bit.lstrip('b')
    show_bit = list(show_bit)
    if show_bit[-1] not in ends:
        show_bit.append('w')
    if show_bit[0] not in starts:
        show_bit.insert(0, 'm')
    return ''.join(show_bit)

def add_adj_for_ngram(show, gramsize):
    """
    If there's a gramsize of more than 1, remake show
    for ngramming
    """
    if gramsize == 1:
        return show
    out = []
    for i in show:
        out.append(i)
    for i in range(1, gramsize):
        for bit in show:
            out.append('+%d%s' % (i, bit))
    return out

def fix_show(show, gramsize):
    """
    Lowercase anything in show and turn into list
    """
    if isinstance(show, list):
        show = [i.lower() for i in show]
    elif isinstance(show, STRINGTYPE):
        show = show.lower()
        show = [show]
    show = [fix_show_bit(i) for i in show]
    return add_adj_for_ngram(show, gramsize)

def interrogator(corpus, 
    search='w', 
    query='any',
    exclude=False,
    excludemode='any',
    searchmode='all',
    show=['w'],
    case_sensitive=False,
    subcorpora=False,
    just=False,
    skip=False,
    lemmatag=False,
    multiprocess=False,
    regex_nonword_filter=r'[A-Za-z0-9]',
    no_closed=False,
    no_punct=True,
    **kwargs):
    """
    Interrogate corpus, corpora, subcorpus and file objects.
    See corpkit.interrogation.interrogate() for docstring
    """

    coref = kwargs.pop('coref', False)

    nosubmode = subcorpora is None
    #todo: temporary
    #if getattr(corpus, '_dlist', False):
    #    subcorpora = 'file'

    # store kwargs and locs
    locs = locals().copy()
    locs.update(kwargs)
    locs.pop('kwargs', None)

    import codecs
    import signal
    import os
    from time import localtime, strftime
    from collections import Counter

    import pandas as pd
    from pandas import DataFrame, Series

    from corpkit.interrogation import Interrogation
    from corpkit.corpus import File, Corpus, Subcorpus
    from corpkit.process import (tregex_engine, get_deps, unsplitter, sanitise_dict, 
                                 animator, filtermaker, fix_search,
                                 pat_format, auto_usecols, format_tregex,
                                 make_conc_lines_from_whole_mid)
    from corpkit.other import as_regex
    from corpkit.dictionaries.process_types import Wordlist
    from corpkit.build import check_jdk
    from corpkit.conll import pipeline
    from corpkit.process import delete_files_and_subcorpora
    
    have_java = check_jdk()

    # remake corpus without bad files and folders 
    corpus, skip, just = delete_files_and_subcorpora(corpus, skip, just)

    # so you can do corpus.interrogate('features/postags/wordclasses/lexicon')
    if search == 'features':
        search = 'v'
        query = 'any'
    if search in ['postags', 'wordclasses']:
        query = 'any'
        show = 'p' if search == 'postags' else 'x'
        # use tregex if simple because it's faster
        # but use dependencies otherwise
        search = 't' if not subcorpora and not just and not skip and have_java else {'w': 'any'}
    if search == 'lexicon':
        search = 't' if not subcorpora and not just and not skip and have_java else {'w': 'any'}
        query = 'any'
        show = ['w']

    if not kwargs.get('cql') and isinstance(search, STRINGTYPE) and len(search) > 3:
        raise ValueError('search argument not recognised.')

    import re
    if regex_nonword_filter:
        is_a_word = re.compile(regex_nonword_filter)
    else:
        is_a_word = re.compile(r'.*')

    from traitlets import TraitError

    # convert cql-style queries---pop for the sake of multiprocessing
    cql = kwargs.pop('cql', None)
    if cql:
        from corpkit.cql import to_corpkit
        search, exclude = to_corpkit(search)

    def signal_handler(signal, _):
        """
        Allow pausing and restarting whn not in GUI
        """
        if root:
            return  
        import signal
        import sys
        from time import localtime, strftime
        signal.signal(signal.SIGINT, original_sigint)
        thetime = strftime("%H:%M:%S", localtime())
        INPUTFUNC('\n\n%s: Paused. Press any key to resume, or ctrl+c to quit.\n' % thetime)
        time = strftime("%H:%M:%S", localtime())
        print('%s: Interrogation resumed.\n' % time)
        signal.signal(signal.SIGINT, signal_handler)

    def ispunct(s):
        import string
        return all(c in string.punctuation for c in s)

    def uniquify(conc_lines):
        """get unique concordance lines"""
        from collections import OrderedDict
        unique_lines = []
        checking = []
        for index, (_, speakr, start, middle, end) in enumerate(conc_lines):
            joined = ' '.join([speakr, start, 'MIDDLEHERE:', middle, ':MIDDLEHERE', end])
            if joined not in checking:
                unique_lines.append(conc_lines[index])
            checking.append(joined)
        return unique_lines

    def compiler(pattern):
        """
        Compile regex or fail gracefully
        """
        if hasattr(pattern, 'pattern'):
            return pattern
        import re
        try:
            if case_sensitive:
                comped = re.compile(pattern)
            else:
                comped = re.compile(pattern, re.IGNORECASE)
            return comped
        except:
            import traceback
            import sys
            from time import localtime, strftime
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lst = traceback.format_exception(exc_type, exc_value, exc_traceback)
            error_message = lst[-1]
            thetime = strftime("%H:%M:%S", localtime())
            print('%s: Query %s' % (thetime, error_message))
            if root:
                return 'Bad query'
            else:
                raise ValueError('%s: Query %s' % (thetime, error_message))

    def get_tregex_values(show):
        """If using Tregex, set appropriate values

        - Check for valid query
        - Make 'any' query
        - Make list query
        """

        translated_option = 't'
        if isinstance(search['t'], Wordlist):
            search['t'] = list(search['t'])
        q = tregex_engine(corpus=False,
                          query=search.get('t'),
                          options=['-t'],
                          check_query=True,
                          root=root
                         )

        # so many of these bad fixing loops!
        nshow = []
        for i in show:
            if i == 'm':
                nshow.append('w')
            else:
                nshow.append(i.lstrip('m'))
        show = nshow

        if q is False:
            if root:
                return 'Bad query', None
            else:
                return 'Bad query', None

        if isinstance(search['t'], list):
            regex = as_regex(search['t'], boundaries='line', case_sensitive=case_sensitive)
        else:
            regex = ''

        # listquery, anyquery, translated_option
        treg_dict = {'p': [r'__ < (/%s/ !< __)' % regex, r'__ < (/.?[A-Za-z0-9].?/ !< __)', 'u'],
                     'pl': [r'__ < (/%s/ !< __)' % regex, r'__ < (/.?[A-Za-z0-9].?/ !< __)', 'u'],
                     'x': [r'__ < (/%s/ !< __)' % regex, r'__ < (/.?[A-Za-z0-9].?/ !< __)', 'u'],
                     't': [r'__ < (/%s/ !< __)' % regex, r'__ < (/.?[A-Za-z0-9].?/ !< __)', 'o'],
                     'w': [r'/%s/ !< __' % regex, r'/.?[A-Za-z0-9].?/ !< __', 't'],
                     'c': [r'/%s/ !< __'  % regex, r'/.?[A-Za-z0-9].?/ !< __', 'C'],
                     'l': [r'/%s/ !< __'  % regex, r'/.?[A-Za-z0-9].?/ !< __', 't'],
                     'u': [r'/%s/ !< __'  % regex, r'/.?[A-Za-z0-9].?/ !< __', 'v']
                    }

        newshow = []

        listq, anyq, translated_option = treg_dict.get(show[0][-1].lower())
        newshow.append(translated_option)
        for item in show[1:]:
            _, _, noption = treg_dict.get(item.lower())
            newshow.append(noption)

        if isinstance(search['t'], list):
            search['t'] = listq
        elif search['t'] == 'any':   
            search['t'] = anyq
        return search['t'], newshow

    def goodbye_printer(return_it=False, only_conc=False):
        """Say goodbye before exiting"""
        if not kwargs.get('printstatus', True):
            return
        thetime = strftime("%H:%M:%S", localtime())
        if only_conc:
            finalstring = '\n\n%s: Concordancing finished! %s results.' % (thetime, format(len(conc_df), ','))
        else:
            finalstring = '\n\n%s: Interrogation finished!' % thetime
            if countmode:
                finalstring += ' %s matches.' % format(tot, ',')
            else:
                finalstring += ' %s unique results, %s total occurrences.' % (format(numentries, ','), format(total_total, ','))
        if return_it:
            return finalstring
        else:
            print(finalstring)

    def make_progress_bar(corpus_iter):
        """generate a progress bar"""

        total_files = len(corpus_iter)

        par_args = {'printstatus': kwargs.get('printstatus', True),
                    'root': root, 
                    'note': note,
                    #'quiet': quiet,
                    'length': total_files,
                    'startnum': kwargs.get('startnum'),
                    'denom': kwargs.get('denominator', 1)}

        term = None
        if kwargs.get('paralleling', None) is not None:
            from blessings import Terminal
            term = Terminal()
            par_args['terminal'] = term
            par_args['linenum'] = kwargs.get('paralleling')

        if in_notebook:
            par_args['welcome_message'] = welcome_message

        outn = kwargs.get('outname', '')
        if outn:
            outn = getattr(outn, 'name', outn)
            outn = outn + ': '

        tstr = '%s%d/%d' % (outn, current_iter, total_files)
        p = animator(None, None, init=True, tot_string=tstr, **par_args)
        tstr = '%s%d/%d' % (outn, current_iter + 1, total_files)
        animator(p, current_iter, tstr, **par_args)
        return p, outn, total_files, par_args

    # find out if using gui
    root = kwargs.get('root')
    note = kwargs.get('note')
    language_model = kwargs.get('language_model')

    # set up pause method
    original_sigint = signal.getsignal(signal.SIGINT)
    if kwargs.get('paralleling', None) is None:
        if not root:
            original_sigint = signal.getsignal(signal.SIGINT)
            signal.signal(signal.SIGINT, signal_handler)

    # wipe non essential class attributes to not bloat query attrib
    if isinstance(corpus, Corpus):
        import copy
        corpus = copy.copy(corpus)
        for k, v in corpus.__dict__.items():
            if isinstance(v, Interrogation):
                corpus.__dict__.pop(k, None)

    # figure out how the user has entered the query and show, and normalise
    from corpkit.process import searchfixer
    search = searchfixer(search, query)

    # instantiate lemmatiser if need be
    lem_instance = False
    if isinstance(search, dict) and search.get('t'):
        from nltk.stem.wordnet import WordNetLemmatizer
        lem_instance = WordNetLemmatizer()

    search = fix_search(search, case_sensitive=case_sensitive, root=root)
    exclude = fix_search(exclude, case_sensitive=case_sensitive, root=root)

    datatype = getattr(corpus, 'datatype', 'conll')
    singlefile = getattr(corpus, 'singlefile', False)

    optiontext = "Searching parsed data"

    locs['search'] = search
    locs['exclude'] = exclude
    locs['query'] = query
    locs['corpus'] = corpus
    locs['multiprocess'] = multiprocess
    locs['print_info'] = kwargs.get('printstatus', True)
    locs['subcorpora'] = subcorpora
    #locs['cname'] = cname
    locs['optiontext'] = optiontext
    locs['mainpath'] = getattr(corpus, 'path', False)

    if multiprocess and not kwargs.get('mp'):
        signal.signal(signal.SIGINT, original_sigint)
        from corpkit.multiprocess import pmultiquery
        return pmultiquery(**locs)
    
    # store all results in here
    from collections import defaultdict, Counter
    
    results = []
    
    count_results = defaultdict(list)
    conc_results = defaultdict(list)

    # check if just counting, turn off conc if so
    countmode = kwargs.get('count')

    # where we are at in interrogation
    current_iter = 0

    # multiprocessing progress bar
    denom = kwargs.get('denominator', 1)
    startnum = kwargs.get('startnum', 0)
    
    # Set some Tregex-related values
    translated_option = False
    if search.get('t'):
        query, translated_option = get_tregex_values(show)
        if query == 'Bad query' and translated_option is None:
            if root:
                return 'Bad query'
            else:
                return
    # more tregex options
    #if tree_to_text:
    #    treg_q = r'ROOT << __'
    #    op = ['-o', '-t', '-w', '-f']
    #elif simple_tregex_mode:
    #    treg_q = search['t']
    #    op = ['-%s' % i for i in translated_option] + ['-o', '-f']

    try:
        nam = get_ipython().__class__.__name__
        if nam == 'ZMQInteractiveShell':
            in_notebook = True
        else:
            in_notebook = False
    except TraitError:
        in_notebook = False
    except ImportError:
        in_notebook = False
    # caused in newest ipython
    except AttributeError:
        in_notebook = False
    except NameError:
        in_notebook = False

    lemtag = False
    if search.get('t'):
        from corpkit.process import gettag
        lemtag = gettag(search.get('t'), lemmatag)

    usecols = auto_usecols(search, exclude, show, kwargs.pop('usecols', None), coref=coref)

    # make the iterable, which should be very simple now
    corpus_iter = corpus.all_files if getattr(corpus, 'all_files', False) else corpus

    # print welcome message
    welcome_message = welcome_printer(search, 'corpus', optiontext, return_it=in_notebook, printstatus=kwargs.get('printstatus', True))

    # create a progress bar
    p, outn, total_files, par_args = make_progress_bar(corpus_iter)

    # if tgrep, make compiled query
    compiled_tgrep = False
    if search.get('t'):
        qstring = search.get('t')
        from nltk.tgrep import tgrep_compile
        compiled_tgrep = tgrep_compile(qstring)

    for f in corpus_iter:

        res = pipeline(fobj=f,
                       search=search,
                       show=show,
                       exclude=exclude,
                       excludemode=excludemode,
                       searchmode=searchmode,
                       case_sensitive=case_sensitive,
                       no_punct=no_punct,
                       no_closed=no_closed,
                       coref=coref,
                       countmode=countmode,
                       is_a_word=is_a_word,
                       subcorpora=subcorpora,
                       just=just,
                       skip=skip,
                       translated_option=translated_option,
                       usecols=usecols,
                       lem_instance=lem_instance,
                       lemtag=lemtag,
                       corpus_name=getattr(corpus, 'corpus_name', False),
                       corpus=corpus,
                       matches=results,
                       multiprocess=kwargs.get('mp'),
                       compiled_tgrep=compiled_tgrep,
                       **kwargs)
            
        if res == 'Bad query':
            return 'Bad query'

        results += res

        # update progress bar
        current_iter += 1
        tstr = '%s%d/%d' % (outn, current_iter + 1, total_files)
        animator(p, current_iter, tstr, **par_args)

    querybits = {'search': search,
                  'exclude': exclude,
                  'subcorpora': subcorpora}

    signal.signal(signal.SIGINT, original_sigint)

    if kwargs.get('paralleling', None) is None:
        interro = Interrogation(data=results, corpus=corpus, query=querybits)
        return interro
    else:
        return results
