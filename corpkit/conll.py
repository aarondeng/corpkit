"""
Process CONLL formatted data

todo:
- adj and corefs back into pipeline
- account for order

"""

def parse_conll(f, first_time=False):
    """take a file and return pandas dataframe with multiindex"""
    import pandas as pd
    import StringIO

    # go to corpkit.constants to modify the order of columns if yours are different
    from corpkit.constants import CONLL_COLUMNS as head
    
    with open(f, 'r') as fo:
        data = fo.read().strip('\n')
    splitdata = []
    metadata = {}
    count = 1
    for sent in data.split('\n\n'):
        metadata[count] = {}
        for line in sent.split('\n'):
            if line and not line.startswith('#'):
                splitdata.append('\n%s' % line)
            else:
                line = line.lstrip('# ')
                if '=' in line:
                    field, val = line.split('=', 1)
                    metadata[count][field] = val
        count += 1

    # determine the number of columns we need
    l = len(splitdata[0].strip('\t').split('\t'))
    head = head[:l]
    
    # if formatting for the first time, add sent ids
    if first_time:
        for i, d in enumerate(splitdata, start=1):
            d = d.replace('\n', '\n%s\t' % str(i))
            splitdata[i-1] = d

    # turn into something pandas can read    
    data = '\n'.join(splitdata)
    data = data.replace('\n\n', '\n') + '\n'

    # open with sent and token as multiindex
    df = pd.read_csv(StringIO.StringIO(data), sep='\t', header=None, names=head, index_col=['s', 'i'])
    df._metadata = metadata
    return df

def get_dependents_of_id(ind, df=False, repeat=False):
    """get governors of a token"""
    
    sent_id, tok_id = getattr(idx, 'name', idx)

    try:
        deps = df.ix[(sent_id, tok_id)]['d'].split(',')
        return [(sent_id, int(d)) for d in deps]
    except:
        justgov = df.loc[df['g'] == tok_id].xs(sent_id, level='s', drop_level=False)
        #print(df.ix[sent_id, tok_id]['w'])
        #for i, x in list(justgov.index):
        #    print(df.ix[sent_id, tok_id]['w'], df.ix[i, x]['w'])
        if repeat is not False:
            return [justgov.index[repeat - 1]]
        else:
            return list(justgov.index)

def get_governors_of_id(idx, df=False, repeat=False, attr=False):
    """get governors of a token"""
    
    sent_id, tok_id = getattr(idx, 'name', idx)
    govid = df.ix[sent_id, tok_id]['g']
    if attr:
        return getattr(df.ix[sent_id,govid], attr, 'root')
    return [(sent_id, govid)]

    #sent = df.xs(sent_id, level='s', drop_level=False)
    #res = list(i for i, tk in sent.iterrows() if tk['g'] == tok_id)
    #if repeat is not False:
    #    return [res[repeat-1]]
    #else:
    #    return res

def get_match(idx, df=False, repeat=False, attr=False, **kwargs):
    """dummy function"""
    sent_id, tok_id = getattr(idx, 'name', idx)
    if attr:
        #print(df[attr].ix[sent_id, tok_id])
        return df[attr].ix[sent_id, tok_id]
    return [(sent_id, tok_id)]

def get_head(idx, df=False, repeat=False):

    sent_id, tok_id = getattr(idx, 'name', idx)

    token = df.ix[sent_id, tok_id]
    if not hasattr(token, 'c'):
        # this should error, because the data isn't there at all
        return [(sent_id, tok_id)]
    elif token['c'] == '_':
        return [(sent_id, tok_id)]
    else:
        just_same_coref = df.loc[df['c'] == token['c'] + '*']
        if not just_same_coref.empty:
            return [just_same_coref.iloc[0].name]
        else:
            return [(sent_id, tok_id)]

def get_conc_start_end(df, only_format_match, show, idx, new_idx):
    """return the left and right context of a concordance line"""

    sent_id, tok_id = idx
    new_sent, new_tok = new_idx
    
    # potentially need to re-enable for head search
    #sent = df.xs(sent_id, level='s', drop_level=False)
    sent = df.ix[sent_id]

    if only_format_match:

        # very optimised by trial and error!
        start = ' '.join(sent['w'][:tok_id])
        end = ' '.join(sent['w'][new_tok+1:])

        return start, end
    # if formatting the whole line, we have to be recursive
    else:
        start = []
        end = []
        # iterate over the words in the sentence
        for t in list(sent.index):
            # show them as we did the match
            out = show_this(df, [(sent_id, t)], show, df._metadata, conc=False)
            if not out:
                continue
            else:
                out = out[0]
            # are these exactly right?
            if t < tok_id:
                start.append(str(out[0]))
            elif t > new_tok:
                end.append(str(out[0]))
        return ' '.join(start), ' '.join(end)

def get_all_corefs(df, coref, s, i):
    if not coref:
        return [(s, i)]
    try:
        just_same_coref = df.loc[df['c'] == df.ix[s,i]['c'] + '*']
        return list(just_same_coref.index)
    except:
        return [(s, i)]

def get_adjacent_token(df, idx, adjacent, opposite=False):
            
    import operator
    
    if opposite:
        mapping = {'-': operator.add, '+': operator.sub}
    else:
        mapping = {'+': operator.add, '-': operator.sub}
    
    # save the old bits
    # get the new idx by going back a few spaces
    # is this ok with no_punct? 
    op, spaces = adjacent[0], int(adjacent[1])
    op = mapping.get(op)
    new_idx = (idx[0], op(idx[1], spaces))
    # if it doesn't exist, move on. maybe wrong?
    try:
        new_token = df.ix[new_idx]
    except IndexError:
        return False, False

    return new_token, new_idx

def search_this(df, obj, attrib, pattern, adjacent=False, coref=False):
    """search the dataframe for a single criterion"""
    
    import re
    # this stores indexes (sent, token) of matches

    # cut down to just tokens with matching attr
    matches = df[df[attrib].str.contains(pattern)]

    # functions for getting the needed object
    revmapping = {'g': get_dependents_of_id,
                  'd': get_governors_of_id,
                  'm': get_match,
                  'h': get_head}

    getfunc = revmapping.get(obj)

    # make a large flat list of all results, taking corefs into account
    every_match = [get_all_corefs(df, coref, *idx) for idx in list(matches.index)]
    every_match = [i for s in every_match for i in s]

    matches = []

    for idx in every_match:
        
        if adjacent:
            idx = get_adjacent_token(df, idx, adjacent, opposite=True)

        for mindex in getfunc(idx, df=df):
            if mindex:
                matches.append(mindex)

    return list(set(matches))

def show_fix(show):
    """show everything"""
    objmapping = {'d': get_dependents_of_id,
                  'g': get_governors_of_id,
                  'm': get_match,
                  'h': get_head}

    out = []
    for val in show:
        adj, val = determine_adjacent(val)
        obj, attr = val[0], val[-1]
        obj_getter = objmapping.get(obj)
        out.append(adj, val, obj, attr, obj_getter)
    return out

def dummy(x, *args, **kwargs):
    return x

def make_not_ofm_concs(df, out, matches, conc, metadata, 
               show, gotten_tok_bits, **kwargs):
    """
    df: all data
    out_mx: indexes for each show val
    out: processed bits for each show val
    """
    fname = kwargs.get('filename', '')
    only_format_match = kwargs.get('only_format_match', False)
    conc_lines = []

    if not conc:
        return conc_lines
    if only_format_match:
        return conc_lines

    df = df['w']
    for (s, i), form in zip(matches, list(gotten_tok_bits)):
        if (s, i) not in matches:
            continue
        if only_format_match:
            sent = df.loc[s]
            start = ' '.join(list(sent.loc[:i-1][0]))
            end = ' '.join(list(sent.loc[i+1:][0]))
        else:
            sent = gotten_tok_bits.loc[s].sort_index()
            start = list(sent.loc[:i-1])
            end = list(sent.loc[i+1:])
        line = [fname, metadata[s]['speaker'], start, [form], end]
        conc_lines.append(line)
    return conc_lines

def format_toks(to_process, show, df):

    import pandas as pd

    objmapping = {'d': get_dependents_of_id,
                  'g': get_governors_of_id,
                  'm': get_match,
                  'h': get_head}
    sers = []
    for val in show:
        obj, attr = val[0], val[-1]
        func = objmapping.get(obj, dummy)
        out = []
        for ix in list(to_process.index):
            if obj == 'm':
                piece = df.loc[ix][attr]
            else:
                piece = func(ix, df=df, attr=attr)
            out.append(piece)
        ser = pd.Series(out, index=to_process.index)
        #print(ser.values)
        ser.name = val
        sers.append(ser)

    dx = pd.concat(sers, axis=1)
    if len(dx.columns) == 1:
        return dx.iloc[:,0]
    else:
        return dx.apply('/'.join, axis=1)

def make_concx(series, matches, metadata, df, conc, **kwargs):
    
    conc_lines = []
    fname = kwargs.get('filename', '')
    if not conc:
        return conc_lines
    
    #maxc, cconc = kwargs.get('maxconc', (False, False))
    #if maxc and maxc < cconc:
    #    return []

    for s, i in matches:
        sent = df.loc[s]
        if kwargs.get('only_format_match'):
            start = ' '.join(list(sent.loc[:i-1]['w']))
            end = ' '.join(list(sent.loc[i+1:]['w']))
        else:
            start = ' '.join(list(series.loc[s,:i-1]))
            end = ' '.join(list(series.loc[s,i+1:]))
        middle = series[s, i]
        sname = metadata[s]['speaker']
        conc_lines.append([fname, sname, start, middle, end])

    return conc_lines

def make_simple_conc(df, matches, formatted):
    return []

def show_this(df, matches, show, metadata, conc=False, coref=False, **kwargs):

    matches = sorted(matches)

    # attempt to leave really fast
    if kwargs.get('countmode'):
        return len(matches), []
    if show in [['mw'], ['mp'], ['ml'], ['mi']] and not conc:
        return list(df.loc[matches][show[0][-1]]), []

    only_format_match = kwargs.get('only_format_match', True)

    if not conc:
        def dummy(x, **kwargs):
            return [x]

        def get_gov(line, df=False, attr=False):
            return getattr(df.ix[line.name[0], df.ix[line.name]['g']], attr, 'root')


        objmapping = {'d': get_dependents_of_id,
                      'g': get_governors_of_id,
                      'm': dummy,
                      'h': get_head}        

        out = []
        from collections import defaultdict
        conc_out = defaultdict(list)

        for val in show:
            obj, attr = val[0], val[-1]
            func = objmapping.get(obj, dummy)
            
            # process everything, if we have to 
            cut_short = False
            if conc and not only_format_match:
                cut_short = True
                newm = list(df.index)
            else:
                newm = matches

            mx = [func(idx, df=df) for idx in newm]    
            mx = [item for sublist in mx for item in sublist]
            
            # a pandas object with the token pieces, ready to join together
            # but it contains all tokens if cut_short mode
            gotten_tok_bits = df.loc[mx][attr.replace('x', 'p')].dropna()
            
            # if gotten_tok_bits contains every token, we can
            # get just the matches from it
            if cut_short:
                gotten = df.loc[matches]
            else:
                gotten = gotten_tok_bits

            # add out actual matches
            out.append(list(gotten))

        formatted = ['/'.join(x) for x in zip(*out)]

        return formatted, []



    # determine params

    process_all = conc and not only_format_match

    # tokens that need formatting
    if not process_all:
        to_process = df.loc[matches]
    else:
        to_process = df
    
    # make a series of formatted data
    series = format_toks(to_process, show, df)
 
    # make a series of tokens, nicely or not nicely formatted

    # generate conc
    conc_lines = make_concx(series, matches, metadata, df, conc, **kwargs)

    return list(series), conc_lines

    # from here on down is a total bottleneck, so it's not used right now.

    easy_attrs = ['w', 'l', 'p', 'f', 'y', 'z']
    strings = []
    concs = []
    # for each index tuple

    

    for idx in matches:
        # we have to iterate over if we have dependent showing
        repeats = len(get_dependents_of_id(idx, df=df)) if any(x.startswith('d') for x in show) else 1
        for repeat in range(1, repeats + 1):
            single_token_bits = []
            matched_idx = False
            for val in show:
                
                adj, val = determine_adjacent(val)
                
                obj, attr = val[0], val[-1]
                obj_getter = objmapping.get(obj)
                
                if adj:
                    new_token, new_idx = get_adjacent_token(df, idx, adj)
                else:
                    new_idx = idx

                if not new_idx in df.index:
                    continue

                # get idxs to show
                matched_idx = obj_getter(new_idx, df=df, repeat=repeat)
                
                # should it really return a list if we never use all bits?
                if not matched_idx:
                    single_token_bits.append('none')
                else:
                    matched_idx = matched_idx[0]
                    piece = False
                    if attr == 's':
                        piece = str(matched_idx[0])
                    elif attr == 'i':
                        piece = str(matched_idx[1])
                    
                    # this deals
                    if matched_idx[1] == 0:
                        if df.ix[matched_idx].name == 'w':
                            if len(show) == 1:
                                continue
                            else:
                                piece = 'none'
                        elif attr in easy_attrs:
                            piece = 'root'
                    else:
                        if not piece:
                            wcmode = False
                            if attr == 'x':
                                wcmode = True
                                attr = 'p'
                            try:
                                piece = df.ix[matched_idx]
                                if not hasattr(piece, attr):
                                    continue
                                piece = piece[attr].replace('/', '-slash-')
                            except IndexError:
                                continue
                            except KeyError:
                                continue
                            if wcmode:
                                from corpkit.dictionaries.word_transforms import taglemma
                                piece = taglemma.get(piece.lower(), piece.lower())
                    single_token_bits.append(piece)

            out = '/'.join(single_token_bits)
            strings.append(out)
            if conc and matched_idx:
                start, end = get_conc_start_end(df, only_format_match, show, idx, new_idx)
                fname = kwargs.get('filename', '')
                sname = metadata[idx[0]].get('speaker', 'none')
                if all(x == 'none' for x in out.split('/')):
                    continue
                if not out:
                    continue
                concs.append([fname, sname, start, out, end])

    strings = [i for i in strings if i and not all(x == 'none' for x in i.split('/'))]
    return strings, concs

def fix_show_bit(show_bit):
    """take a single search/show_bit type, return match"""
    #show_bit = [i.lstrip('n').lstrip('b') for i in show_bit]
    ends = ['w', 'l', 'i', 'n', 'f', 'p', 'x', 'r', 's']
    starts = ['d', 'g', 'm', 'n', 'b', 'h', '+', '-']
    show_bit = show_bit.lstrip('n')
    show_bit = show_bit.lstrip('b')
    show_bit = list(show_bit)
    if show_bit[-1] not in ends:
        show_bit.append('w')
    if show_bit[0] not in starts:
        show_bit.insert(0, 'm')
    return ''.join(show_bit)


def remove_by_mode(matches, mode, criteria):
    """if mode is all, remove any entry that occurs < len(criteria)"""
    out = []
    if mode == 'all':
        from collections import Counter
        counted = Counter(matches)
        for w in matches:
            if counted[w] == len(criteria):
                if w not in out:
                    out.append(w)
    elif mode == 'any':
        for w in matches:
            if w not in out:
                out.append(w)        
    return out

def determine_adjacent(original):
    if original[0] in ['+', '-']:
        adj = (original[0], original[1:-2])
        original = original[-2:]
    else:
        adj = False
    return adj, original

def process_df_for_speakers(df, metadata, just_speakers, coref=False):
    """
    keep just the correct speakers
    """
    if not just_speakers:
        return df
    # maybe could be sped up, but let's not for now:
    if coref:
        return df
    import re
    good_sents = []
    new_metadata = {}
    for sentid, data in sorted(metadata.items()):
        speaker = data.get('speaker')
        if isinstance(just_speakers, list):
            if speaker in just_speakers:
                good_sents.append(sentid)
                new_metadata[sentid] = data
        elif isinstance(just_speakers, (re._pattern_type, str)):
            if re.search(just_speakers, speaker):
                good_sents.append(sentid)
                new_metadata[sentid] = data
    df = df.loc[good_sents]
    df._metadata = new_metadata
    return df

def pipeline(f,
             search,
             show,
             exclude=False,
             searchmode='all',
             excludemode='any',
             conc=False,
             coref=False,
             **kwargs):
    """a basic pipeline for conll querying---some options still to do"""

    # make file into df, get metadata
    # restrict for speakers
    # remove punct/closed words
    # get indexes of matches for every search
    # remove if not enough matches or exclude is defined
    # show: (bottleneck)
    #
    # issues: get dependents, coref, adjacent, conc, only_format_match

    all_matches = []
    all_exclude = []

    if isinstance(show, str):
        show = [show]
    show = [fix_show_bit(i) for i in show]

    df = parse_conll(f)

    df = process_df_for_speakers(df, df._metadata, kwargs.get('just_speakers'), coref=coref)
    metadata = df._metadata

    # need to get rid of brackets too ...
    if kwargs.get('no_punct', False):
        df = df[df['w'].str.contains(kwargs.get('is_a_word', r'[A-Za-z0-9]'))]
        # find way to reset the 'i' index ...

    if kwargs.get('no_closed'):
        from corpkit.dictionaries import wordlists
        crit = wordlists.closedclass.as_regex(boundaries='l')
        df = df[~df['w'].str.lower.contains(crit)]

    
    for k, v in search.items():

        adj, k = determine_adjacent(k)
        
        res = search_this(df, k[0], k[-1], v, adjacent=adj, coref=coref)
        for r in res:
            all_matches.append(r)

    all_matches = remove_by_mode(all_matches, searchmode, search)
    
    if exclude:
        for k, v in exclude.items():
            adj, k = determine_adjacent(k)
            res = search_this(df, k[0], k[-1], v, adjacent=adj, coref=coref)
            for r in res:
                all_exclude.append(r)

        all_exclude = remove_by_mode(all_exclude, excludemode, exclude)
        
        # do removals
        for i in all_exclude:
            try:
                all_matches.remove(i)
            except ValueError:
                pass

    return show_this(df, all_matches, show, metadata, conc, coref=coref, **kwargs)


def load_raw_data(f):
    """loads the stripped and raw versions of a parsed file"""

    # open the unparsed version of the file, read into memory
    stripped_txtfile = f.replace('.conll', '').replace('-parsed', '-stripped')
    with open(stripped_txtfile, 'r') as old_txt:
        stripped_txtdata = old_txt.read()

    # open the unparsed version with speaker ids
    id_txtfile = f.replace('.conll', '').replace('-parsed', '')
    with open(id_txtfile, 'r') as idttxt:
        id_txtdata = idttxt.read()

    return stripped_txtdata, id_txtdata

def get_speaker_from_offsets(stripped, plain, sent_offsets):
    if not stripped and not plain:
        return 'none'
    start, end = sent_offsets
    sent = stripped[start:end]
    # find out line number
    # sever at start of match
    cut_old_text = stripped[:start]
    line_index = cut_old_text.count('\n')
    # lookup this text
    with_id = plain.splitlines()[line_index]
    split_line = with_id.split(': ', 1)
    if len(split_line) > 1:
        speakerid = split_line[0]
    else:
        speakerid = 'UNIDENTIFIED'
    return speakerid


def convert_json_to_conll(path, speaker_segmentation=False, coref=False):
    """
    take json corenlp output and convert to conll, with
    dependents, speaker ids and so on added.
    """

    import json
    import re
    from corpkit.build import get_filepaths

    files = get_filepaths(path, ext='conll')
    
    for f in files:

        if speaker_segmentation:
            stripped, raw = load_raw_data(f)
        else:
            stripped, raw = None, None

        main_out = ''
        with open(f, 'r') as fo:
            data = json.load(fo)

        ref = 1
        for idx, sent in enumerate(data['sentences'], start=1):
            tree = sent['parse'].replace('\n', '')
            tree = re.sub(r'\s+', ' ', tree)

            # offsets for speaker_id
            sent_offsets = (sent['tokens'][0]['characterOffsetBegin'], \
                            sent['tokens'][-1]['characterOffsetEnd'])
            speaker = get_speaker_from_offsets(stripped, raw, sent_offsets)
            output = '# sent_id %d\n# parse=%s\n# speaker=%s\n' % (idx, tree, speaker)
            
            for token in sent['tokens']:
                index = str(token['index'])
                governor, func = next((str(i['governor']), str(i['dep'])) \
                                         for i in sent['basic-dependencies'] \
                                         if i['dependent'] == int(index))
                depends = [str(i['dependent']) for i in sent['basic-dependencies'] if i['governor'] == int(index)]
                if not depends:
                    depends = '0'
                #offsets = '%d,%d' % (token['characterOffsetBegin'], token['characterOffsetEnd'])
                line = [str(idx),
                        index,
                        token['word'],
                        token['lemma'],
                        token['pos'],
                        token['ner'],
                        governor,
                        func,
                        ','.join(depends)]
                #if coref:
                #    refmatch = get_corefs(data, idx, token['index'] + 1, ref)
                #    if refmatch != '_':
                #        ref += 1
                #    sref = str(refmatch)
                #    line.append(sref)
                
                output += '\t'.join(line) + '\n'
            main_out += output + '\n'

        # post process corefs
        if coref:
            import re
            dct = {}
            idxreg = re.compile('^([0-9]+)\t([0-9]+)')
            splitmain = main_out.split('\n')
            # add tab _ to each line, make dict of sent-token: line index
            for i, line in enumerate(splitmain):
                if line and not line.startswith('#'):
                    splitmain[i] += '\t_'
                match = re.search(idxreg, line)
                if match:
                    l, t = match.group(1), match.group(2)
                    dct[(int(l), int(t))] = i
            
            # for each coref chain
            for numstring, list_of_dicts in sorted(data['corefs'].items()):
                # for each mention
                for d in list_of_dicts:
                    snum = d['sentNum']
                    # get head?
                    # this has been fixed in dev corenlp: 'headIndex' --- could simply use that
                    # ref : https://github.com/stanfordnlp/CoreNLP/issues/231
                    for i in range(d['startIndex'], d['endIndex']):
                    
                        try:
                            ix = dct[(snum, i)]
                            fixed_line = splitmain[ix].rstrip('\t_') + '\t%s' % numstring
                            gov_s = int(fixed_line.split('\t')[6])
                            if gov_s < d['startIndex'] or gov_s > d['endIndex']:
                                fixed_line += '*'
                            splitmain[ix] = fixed_line
                            dct.pop((snum, i))
                        except KeyError:
                            pass

            main_out = '\n'.join(splitmain)

        with open(f, 'w') as fo:
            fo.write(main_out)
