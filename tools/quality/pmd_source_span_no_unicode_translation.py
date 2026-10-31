"""Fail-closed JLS25 3.3 zero-translation guard, not a Java lexer or Unicode decoder.

Invariant: no eligible Unicode escape has yet been encountered. Thus no previously
translated character exists, and raw contiguous-backslash parity suffices. Reject
the first eligible backslash followed by u, even if its digits would be malformed.
Never alter Source bytes to make a diagnostic fit.
"""
import re
from pg16291_thread_five_gonefd_two_purpose_v2 import raw_span


def no_translation(text):
    if not isinstance(text,str):raise ValueError('Source text required')
    if any(c in text for c in ('\r','\0','\v','\f','\x1c','\x1d','\x1e','\x85','\u2028','\u2029','\x1a')):
        raise ValueError('ordinary LF lines, no alternative splitlines/EOF controls')
    try:text.encode('utf-8')
    except UnicodeEncodeError as failure:raise ValueError('valid UTF8 Source required') from failure
    backslashes=0
    inert_markers=0
    for index,char in enumerate(text):
        if char=='\\':
            if text[index+1:index+2]=='u':
                if backslashes%2==0:raise ValueError('eligible Unicode escape unresolved')
                inert_markers+=1
            backslashes+=1
        else:backslashes=0
    return inert_markers


def span(text,attributes):
    no_translation(text)
    if not isinstance(attributes,dict):raise ValueError('diagnostic attributes required')
    for key in ('beginline','endline','begincolumn','endcolumn'):
        value=attributes.get(key)
        if not isinstance(value,str) or re.fullmatch(r'[1-9][0-9]*',value) is None:
            raise ValueError('positive decimal one-origin coordinates required')
    return raw_span(text,attributes)
