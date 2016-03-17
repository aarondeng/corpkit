from __future__ import print_function

# in here are functions used internally by corpkit
# not intended to be called by users. 

def datareader(data, plaintext = False, **kwargs):
    import corpkit
    """
    Returns a string of plain text from a number of kinds of data.

    The kinds of data currently accepted are:

    path to corpus : all trees are flattened
    path to subcorpus : all trees are flattened
    conc() output (list of concordance lines)
    csv file generated with conc()
    a string of text
    """
    import os
    import pandas
    from process import tregex_engine
    try:
        get_ipython().getoutput()
    except TypeError:
        have_ipython = True
    except NameError:
        import subprocess
        have_ipython = False

    tregex_engine_used = False
    
    # if unicode, make it a string
    if type(data) == str:
        if not os.path.isdir(data):
            if not os.path.isfile(data):
                return good
    if type(data) == str:
        # if it's a file, read it
        if os.path.isfile(data):
            good = open(data).read()
        # if it's a dir, flatten all trees
        elif os.path.isdir(data):
            # get all sentences newline separated
            query = r'__ !< __'
            options = ['-o', '-t']

            # if lemmatise, we get each word on a newline
            if kwargs.get('lemmatise'):
                query = r'__ <# (__ !< __)'
                options = ['-o']
 
            # check for trees ...
            #while plaintext is False:
                #for f in first_twenty:
                    #plaintext = tregex_engine(corpus = f, check_for_trees = True)
            
            if not plaintext:
                tregex_engine_used = True
                results = tregex_engine(corpus = data,
                                              options = options,
                                              query = query, 
                                              **kwargs)
            else:
                results = []
                fs = [os.path.join(data, f) for f in os.listdir(data)]
                # do recursive if need
                if any(os.path.isdir(f) for f in fs):
                    recursive_files = []
                    for dirname, dirnames, filenames in os.walk(data):
                        for filename in filenames:
                            recursive_files.append(os.path.join(dirname, filename))
                    fs = recursive_files
                
                import nltk
                sent_tokenizer=nltk.data.load('tokenizers/punkt/english.pickle')
                for f in fs:
                    raw = str(open(f).read(), 'utf-8', errors = 'ignore')
                    sents = sent_tokenizer.tokenize(raw)
                    tokenized_sents = [nltk.word_tokenize(i) for i in sents]
                    for sent in tokenized_sents:
                        for w in sent:
                            results.append(w.lower()) 

            return results

            #good = '\n'.join(results)
        # if a string of text, 
        else:
            good = data
    # if conc results, turn into string...
    elif type(data) == pandas.core.frame.DataFrame:
        # if conc lines:
        try:
            if list(data.columns) == ['l', 'm', 'r']:
                conc_lines = True
            else:
                conc_lines = False
        except:
            conc_lines = False
        if conc_lines:
            # may not be unicode!?
            good = [' '.join(list(data.ix[l])) for l in list(data.index)]

    else:
        good = data

    # make unicode
    if not tregex_engine_used:
        try:
            good = str(good, 'utf-8', errors = 'ignore')
        except TypeError:
            pass

    return good

def tregex_engine(corpus = False,  
                  options = False, 
                  query = False, 
                  check_query = False,
                  check_for_trees = False,
                  lemmatise = False,
                  just_content_words = False,
                  return_tuples = False,
                  root = False,
                  preserve_case = False,
                  **kwargs):
    """
    Run a Java Tregex query
    
    :param query: tregex query
    :type query: str
    
    :param options: list of tregex options
    :type options: list of strs -- ['-t', '-o']
    
    :param corpus: place to search
    :type corpus: str
    
    :param check_query: just make sure query ok
    :type check_query: bool
    
    :param check_for_trees: find out if corpus contains parse trees
    :type check_for_trees: bool

    :returns: list of search results

    """
    import corpkit
    from process import add_corpkit_to_path
    add_corpkit_to_path()
    import subprocess 
    from subprocess import Popen, PIPE, STDOUT
    import re
    from time import localtime, strftime
    from process import checkstack
    from dictionaries.word_transforms import wordlist
    import os
    import sys
    pyver = sys.version_info.major
    if pyver == 2:
        inputfunc = raw_input
    elif pyver == 3:
        inputfunc = input

    on_cloud = checkstack('/opt/python/lib')

    def find_wordnet_tag(tag):
        import corpkit
        if tag.startswith('j'):
            tag = 'a'
        elif tag.startswith('v') or tag.startswith('m'):
            tag = 'v'
        elif tag.startswith('n'):
            tag = 'n'
        elif tag.startswith('r'):
            tag = 'r'
        else:
            tag = False
        return tag

    # if check_query, enter the while loop
    # if not, get out of it
    an_error_occurred = True

    # site pack path
    corpath = os.path.join(os.path.dirname(corpkit.__file__))
    cor1 = os.path.join(corpath, 'tregex.sh')
    cor2 = os.path.join(corpath, 'corpkit', 'tregex.sh')

    # pyinstaller
    pyi = sys.argv[0].split('Contents/MacOS')[0] + 'Contents/MacOS/tregex.sh'

    possible_paths = ['tregex.sh', corpath, pyi, cor1, cor2]

    while an_error_occurred:
        tregex_file_found = False
        for i in possible_paths:
            if os.path.isfile(i):
                tregex_command = [i]
                tregex_file_found = True
                break
        if not tregex_file_found:
            thetime = strftime("%H:%M:%S", localtime())
            print("%s: Couldn't find Tregex in %s." % (thetime, ', '.join(possible_paths)))
            return False

        if not query:
            query = 'NP'
        # if checking for trees, use the -T option
        if check_for_trees:
            options = ['-o', '-T']

        filenaming = False
        try:
            if '-f' in options:
                filenaming = True
        except:
            pass

        if return_tuples or lemmatise:
            options = ['-o']
        # append list of options to query 
        if options:
            if '-s' not in options and '-t' not in options:
                options.append('-s')
            [tregex_command.append(o) for o in options]
        # dummy option
        else:
            options = ['-o', '-t']
        if query:
            tregex_command.append(query)
        if corpus:
            if os.path.isdir(corpus) or os.path.isfile(corpus):
                if '-filter' not in options:
                    tregex_command.append(corpus)
        # do query
        #try:
        
        if type(options) != bool:
            if not '-filter' in options:
                res = subprocess.check_output(tregex_command, stderr=subprocess.STDOUT).decode(encoding='UTF-8').splitlines()
            else:
                p = Popen(tregex_command, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
                p.stdin.write(corpus.encode('utf-8', errors = 'ignore'))
                res = p.communicate()[0].decode(encoding='UTF-8').splitlines()
                p.stdin.close()
                print(res)
        else:
            p = Popen(tregex_command, stdout=PIPE, stdin=PIPE, stderr=STDOUT)
            p.stdin.write(corpus.encode('utf-8', errors = 'ignore'))
            res = p.communicate()[0].decode(encoding='UTF-8').splitlines()
            print(type(res))
            p.stdin.close()
        # exception handling for regex error
        #except Exception, e:
        #    try:
        #        res = str(e.output).split('\n')
        #    except:
        #        raise e

        if check_query:
            # define error searches 
            tregex_error = re.compile(r'^Error parsing expression')
            regex_error = re.compile(r'^Exception in thread.*PatternSyntaxException')
            # if tregex error, give general error message
            if re.match(tregex_error, res[0]):
                tregex_error_output = ""
                if root:
                    time = strftime("%H:%M:%S", localtime())
                    print('%s: Error parsing Tregex query.' % time)
                    return False
                time = strftime("%H:%M:%S", localtime())

                selection = inputfunc('\n%s: Error parsing Tregex expression "%s".\nWould you like to:\n\n' \
                    '              a) rewrite it now\n' \
                    '              b) exit\n\nYour selection: ' % (time, query))
                if 'a' in selection:
                    query = inputfunc('\nNew Tregex query: ')
                elif 'b' in selection:
                    print('')
                    return False
            
            # if regex error, try to help
            elif re.match(regex_error, res[0]):
                if root:
                    time = strftime("%H:%M:%S", localtime())
                    print('%s: Regular expression in Tregex query contains an error.' % time)
                    return False
                info = res[0].split(':')
                index_of_error = re.findall(r'index [0-9]+', info[1])
                justnum = index_of_error[0].split('dex ')
                spaces = ' ' * int(justnum[1])
                remove_start = query.split('/', 1)
                remove_end = remove_start[1].split('/', -1)
                time = strftime("%H:%M:%S", localtime())
                selection = inputfunc('\n%s: Error parsing regex inside Tregex query: %s'\
                '. Best guess: \n%s\n%s^\n\nYou can either: \n' \
                '              a) rewrite it now\n' \
                '              b) exit\n\nYour selection: ' % (time, str(info[1]), str(remove_end[0]), spaces))
                if 'a' in selection:
                    query = inputfunc('\nNew Tregex query: ')
                elif 'b' in selection:
                    print('')
                    return                
            else:
                an_error_occurred = False
                return query
        # if not query checking, leave this horrible while loop
        else: 
            an_error_occurred = False
    
    # counting is easy, just get out with the number
    if '-C' in options:
        return int(res[-1])

    # remove errors and blank lines
    res = [s for s in res if not s.startswith('PennTreeReader:') and s]

    # find and remove stderr lines
    if '-filter' not in options:
        n = 1
        std_last_index = res.index(next(s for s in res \
                        if s.startswith('Reading trees from file') \
                        or s.startswith('using default tree')))
    else:
        n = 2
        std_last_index = res.index(next(s for s in res \
                        if s.startswith('Parsed representation:')))
    res = res[std_last_index + n:]
    res = [r.lstrip().rstrip() for r in res]

    # this is way slower than it needs to be, because it searches a whole subcorpus!
    if check_for_trees:
        if res[0].startswith('1:Next tree read:'):
            return True
        else:
            return False
    # return if no matches
    if res[-1] == 'There were 0 matches in total.':
        return []
    # remove total
    res = res[:-1]
    # make unicode and lowercase
    make_tuples = []

    if filenaming:
        for index, r in enumerate(res):
            if r.startswith('# /'):
                make_tuples.append((r, res[index + 1]))
        res = make_tuples
                
    if not filenaming:
        if preserve_case:
            pass # res = [str(w, 'utf-8', errors = 'ignore') for w in res]
        else:
            res = [w.lower().replace('/', '-slash-') for w in res]
    else:
        if preserve_case:
            pass # res = [(str(t, 'utf-8', errors = 'ignore'), str(w, 'utf-8', errors = 'ignore')) for t, w in res]
        else:
            res = [(t, w.lower().replace('/', '-slash-')) for t, w in res]

    if lemmatise or return_tuples:
        # CAN'T BE USED WITH ALMOST EVERY OPTION!
        allwords = []
        from nltk.stem.wordnet import WordNetLemmatizer
        lmtzr=WordNetLemmatizer()
         # turn this into a list of words or lemmas, with or without closed words
        for result in res:
            # remove brackets and split on first space
            result = result.lstrip('(')
            result = result.rstrip(')')
            tag, word = result.split(' ', 1)
            # get wordnet tag from stanford tag
            wordnet_tag = find_wordnet_tag(tag)
            short_tag = tag[:2]
            # do manual lemmatisation first
            if lemmatise:
                if word in wordlist:
                    word = wordlist[word]
                # do wordnet lemmatisation
                if wordnet_tag:
                    word = lmtzr.lemmatize(word, wordnet_tag)
            if just_content_words:
                if wordnet_tag:
                    if return_tuples:
                        allwords.append((word, tag))
                    else:
                        allwords.append(word)
            else:
                if return_tuples:
                    allwords.append((word, tag))
                else:
                    allwords.append(word)
        res = allwords
    if return_tuples:
        res = [(w, t.upper()) for w, t in res]
    return res


def make_nltk_text(directory, 
                   collapse_dirs = True, 
                   tagged = False, 
                   lemmatise = False, 
                   just_content_words = False):
    """
    Turn a lot of trees into an nltk style text"""
    import nltk
    import os
    from process import tregex_engine
    if type(directory) == str:
        dirs = [os.path.join(directory, d) for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]
        if len(dirs) == 0:
            dirs = [directory]
    elif type(directory) == list:
        dirs = directory

    return_tuples = False
    if tagged:
        return_tuples = True

    if just_content_words:
        lemmatise = True

    query = r'__ < (/.?[A-Za-z0-9].?/ !< __)'
    if not return_tuples and not lemmatise:
        options = ['-o', '-t']
    else:
        options = ['-o']

    # filthy code.
    all_out = []

    for d in dirs:
        print("Flattening %s ... " % str(d))
        res = tregex_engine(corpus = d, 
                            query = query, 
                            options = options,
                            lemmatise = lemmatise,
                            just_content_words = just_content_words,
                            return_tuples = return_tuples)
        all_out.append(res)

    if collapse_dirs:
        tmp = []
        for res in all_out:
            for w in res:
                tmp.append(w)
        all_out = tmp
        textx = nltk.Text(all_out)
    else:
        textx = {}
        for name, text in zip(dirs, all_out):
            t = nltk.Text(all_out)
            textx[os.path.basename(name)] = t
    return textx



def show(lines, index, show = 'thread'):
    """show lines.ix[index][link] as frame"""
    import corpkit
    url = lines.ix[index]['link'].replace('<a href=', '').replace('>link</a>', '')
    return HTML('<iframe src=%s width=1000 height=500></iframe>' % url)

def add_corpkit_to_path():
    import sys
    import os
    import inspect
    corpath = inspect.getfile(inspect.currentframe())
    baspat = os.path.dirname(corpath)
    dicpath = os.path.join(baspat, 'dictionaries')
    for p in [corpath, baspat, dicpath]:
        if p not in sys.path:
            sys.path.append(p)
        if p not in os.environ["PATH"].split(':'): 
            os.environ["PATH"] += os.pathsep + p

def add_nltk_data_to_nltk_path(**kwargs):
    import nltk
    import os
    npat = nltk.__file__
    nltkpath = os.path.dirname(npat)
    if nltkpath not in nltk.data.path:
        nltk.data.path.append(nltkpath)
        if 'note' in list(kwargs.keys()):
            path_within_gui = os.path.join(nltkpath.split('/lib/python2.7')[0], 'nltk_data')
            if path_within_gui not in nltk.data.path:
                nltk.data.path.append(path_within_gui)
            if path_within_gui.replace('/nltk/', '/', 1) not in nltk.data.path:
                nltk.data.path.append(path_within_gui.replace('/nltk/', '/', 1))

def get_gui_resource_dir():
    import inspect
    import os
    import sys
    if sys.platform == 'darwin':
        key = 'Mod1'
        fext = 'app'
    else:
        key = 'Control'
        fext = 'exe'
    corpath = corpath = __file__
    extens = '.%s' % fext
    apppath = corpath.split(extens , 1)
    resource_path = ''
    # if not an .app
    if len(apppath) == 1:
        resource_path = os.path.dirname(corpath)
    else:
        apppath = apppath[0] + extens
        appdir = os.path.dirname(apppath)
        if sys.platform == 'darwin':
            #resource_path = os.path.join(apppath, 'Contents', 'Resources')
            resource_path = os.path.join(apppath, 'Contents', 'MacOS')
        else:
            resource_path = appdir
    return resource_path

def get_fullpath_to_jars(path_var):
    """when corenlp is needed, this sets corenlppath as the path to jar files,
    or returns false if not found"""
    import os
    important_files = ['stanford-corenlp-3.5.2-javadoc.jar', 'stanford-corenlp-3.5.2-models.jar',
                   'stanford-corenlp-3.5.2-sources.jar', 'stanford-corenlp-3.5.2.jar']
    
    # if user selected file in parser dir rather than dir,
    # get the containing dir
    path_var_str = path_var.get()

    if os.path.isfile(path_var_str):
        path_var_str = os.path.dirname(path_var_str.rstrip('/'))
    # if the user selected the subdir:
    if all(os.path.isfile(os.path.join(path_var_str, f)) for f in important_files):
        path_var.set(path_var_str)
        return True

    # if the user selected the parent dir:
    if os.path.isdir(path_var_str):
        # get subdirs containing the jar
        try:
            find_install = [d for d in os.listdir(path_var_str) \
                if os.path.isdir(os.path.join(path_var_str, d)) \
                and os.path.isfile(os.path.join(path_var_str, d, 'jollyday.jar'))]
        except OSError:
            pass
        if len(find_install) > 0:
            path_var.set(os.path.join(path_var_str, find_install[0]))
            return True

    # need to fix this duplicated code
    try:
        home = os.path.expanduser("~")
        try_dir = os.path.join(home, 'corenlp')
        if os.path.isdir(try_dir):
            path_var_str = try_dir
            # get subdirs containing the jar
            try:
                find_install = [d for d in os.listdir(path_var_str) \
                    if os.path.isdir(os.path.join(path_var_str, d)) \
                    and os.path.isfile(os.path.join(path_var_str, d, 'jollyday.jar'))]
            except OSError:
                pass
            if len(find_install) > 0:
                path_var.set(os.path.join(path_var_str, find_install[0]))
                return True
    except:
        pass
    return False

def determine_datatype(path):
    """determine if plaintext, tokens or parsed xml"""
    import os
    from collections import Counter
    allowed = ['.txt', '.xml', '.p']
    exts = []
    if not os.path.isdir(path) and not os.path.isfile(path):
        raise ValueError("Corpus path '%s' doesn't exist." % path)
    singlefile = False
    if os.path.isfile(path):
        singlefile = True
        if '.' in path:
            exts = [os.path.splitext(path)[1]]
        else:
            exts = ['.txt']
    else:
        for (root, dirs, fs) in os.walk(path):
            for f in fs:
                if '.' in f:
                    ext = os.path.splitext(f)[1]
                    exts.append(ext)
    counted = Counter(exts)
    counted.pop('', None)
    try:
        mc = counted.most_common(1)[0][0]
    except IndexError:
        mc = '.txt'
    if mc == '.xml':
        return 'parse', singlefile
    elif mc == '.txt':
        return 'plaintext', singlefile
    elif mc == '.p':
        return 'tokens', singlefile
    else:
        return 'plaintext', singlefile

def filtermaker(the_filter, case_sensitive = False):
    import re
    if type(the_filter) == list:
        from other import as_regex
        the_filter = as_regex(the_filter, case_sensitive = case_sensitive)
    try:
        output = re.compile(the_filter)
        is_valid = True
    except:
        is_valid = False
        if root:
            import traceback
            import sys
            exc_type, exc_value, exc_traceback = sys.exc_info()
            lst = traceback.format_exception(exc_type, exc_value,
                          exc_traceback)
            error_message = lst[-1]
            thetime = strftime("%H:%M:%S", localtime())
            print('%s: Filter %s' % (thetime, error_message))
            return 'Bad query'
    
    while not is_valid:
        if root:
            time = strftime("%H:%M:%S", localtime())
            print(the_filter)
            print('%s: Invalid the_filter regular expression.' % time)
            return False
        time = strftime("%H:%M:%S", localtime())
        selection = input('\n%s: filter regular expression " %s " contains an error. You can either:\n\n' \
            '              a) rewrite it now\n' \
            '              b) exit\n\nYour selection: ' % (time, the_filter))
        if 'a' in selection:
            the_filter = input('\nNew regular expression: ')
            try:
                output = re.compile(r'\b' + the_filter + r'\b')
                is_valid = True
            except re.error:
                is_valid = False
        elif 'b' in selection:
            print('')
            return False
    return output

def searchfixer(search, query, datatype = False):
    """normalise query/search value"""
    if type(search) == str and type(query) == dict:
        return search
    if type(search) == str:
        search = search[0].lower()
        if not search.lower().startswith('t') and not search.lower().startswith('n'):
            if query == 'any':
                query = r'.*'
        search = {search: query}
    return search

def is_number(s):
    """check if str can be can be made into float/int"""
    try:
        float(s) # for int, long and float
    except ValueError:
        try:
            complex(s) # for complex
        except ValueError:
            return False
    return True

def animator(progbar, count, tot_string = False, linenum = False, terminal = False, 
             init = False, length = False, **kwargs):
    """
    Animates progress bar in unique position in terminal
    Multiple progress bars not supported in jupyter yet.
    """
    
    # add startnum
    start_at = kwargs.get('startnum', 0)
    if start_at is None:
        start_at = 0.0
    denominator = kwargs.get('denom', 1)
    if kwargs.get('note'):
        if count is None:
            perc_done = 0.0
        else:
            perc_done = (count * 100.0 / float(length)) / float(denominator)
        kwargs['note'].progvar.set(start_at + perc_done)
        kwargs['root'].update()
        return

    if init:
        from textprogressbar import TextProgressBar
        return TextProgressBar(length, dirname = tot_string)
        # this try is for sublime text nosetests, which don't take terminal object
    try:
        with terminal.location(0, terminal.height - (linenum + 1)):
            if tot_string:
                progbar.animate(count, tot_string)
            else:
                progbar.animate(count)
    # typeerror for nose
    except:
        if tot_string:
            progbar.animate(count, tot_string)
        else:
            progbar.animate(count)


def parse_just_speakers(just_speakers, path):
    if just_speakers is True:
        just_speakers = ['each']
    if just_speakers is False or just_speakers is None:
        return False
    if type(just_speakers) == str:
        just_speakers = [just_speakers]
    if type(just_speakers) == list:
        if just_speakers == ['each']:
            from build import get_speaker_names_from_xml_corpus
            just_speakers = get_speaker_names_from_xml_corpus(path)
    return just_speakers


def get_deps(sentence, dep_type):
    if dep_type == 'basic-dependencies':
        return sentence.basic_dependencies
    if dep_type == 'collapsed-dependencies':
        return sentence.collapsed_dependencies
    if dep_type == 'collapsed-ccprocessed-dependencies':
        return sentence.collapsed_ccprocessed_dependencies

def timestring(input):
    """print with time prepended"""
    from time import localtime, strftime
    thetime = strftime("%H:%M:%S", localtime())
    print('%s: %s' % (thetime, input.lstrip()))

def makesafe(variabletext, drop_datatype = True, hyphens_ok = False):
    import re
    from process import is_number
    if hyphens_ok:
        variable_safe_r = re.compile(r'[^A-Za-z0-9_]+', re.UNICODE)
    else:
        variable_safe_r = re.compile(r'[^A-Za-z0-9_-]+', re.UNICODE)
    try:
        txt = variabletext.name.split('.')[0]
    except AttributeError:
        txt = variabletext.split('.')[0]
    if drop_datatype:
        txt = txt.replace('-parsed', '')

    txt = txt.replace(' ', '_')
    variable_safe = re.sub(variable_safe_r, '', txt)
    if is_number(variable_safe):
        variable_safe = 'c' + variable_safe
    return variable_safe

def interrogation_from_conclines(newdata):
    """make new interrogation result from its conc lines"""
    from collections import Counter
    from pandas import DataFrame
    import corpkit
    from corpkit import editor
    results = {}
    conc = newdata
    subcorpora = list(set(conc['c']))
    for subcorpus in subcorpora:
        counted = Counter(list(conc[conc['c'] == subcorpus]['m']))
        results[subcorpus] = counted

    the_big_dict = {}
    unique_results = set([item for sublist in list(results.values()) for item in sublist])
    for word in unique_results:
        the_big_dict[word] = [subcorp_result[word] for name, subcorp_result in sorted(results.items(), key=lambda x: x[0])]
    # turn master dict into dataframe, sorted
    df = DataFrame(the_big_dict, index = sorted(results.keys())) 
    df = editor(df, sort_by = 'total', print_info = False)
    df.concordance = conc
    return df


def checkstack(the_string):
    """checks for pytex"""
    import inspect
    thestack = []
    for bit in inspect.stack():
        for b in bit:
            thestack.append(str(b))
    as_string = ' '.join(thestack)
    if as_string.lower().count(the_string) > 1:
        return True
    else:
        return False

def check_tex(have_ipython = True):
    """see if tex is available"""
    import os
    if have_ipython:
        checktex_command = 'which latex'
        o = get_ipython().getoutput(checktex_command)[0]
        if o.startswith('which: no latex in'):
            have_tex = False
        else:
            have_tex = True
    else:
        import subprocess
        FNULL = open(os.devnull, 'w')
        checktex_command = ["which", "latex"]
        try:
            o = subprocess.check_output(checktex_command, stderr=FNULL)
            have_tex = True
        except subprocess.CalledProcessError:
            have_tex = False
    return have_tex
