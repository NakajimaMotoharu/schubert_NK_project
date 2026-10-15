"""Strict JDK UTF16 source-position consumer, including supplementary prefix boundaries."""


def source_slice(text,start,end):
    if type(text)is not str or type(start)is not int or type(end)is not int or not 0<=start<=end:
        raise ValueError('typed ordered UTF16 source bounds required')
    try:
        raw=text.encode('utf-16-le')
        if 2*end>len(raw):raise ValueError('UTF16 source bounds exceeded')
        raw[:2*start].decode('utf-16-le');raw[:2*end].decode('utf-16-le')
        return raw[2*start:2*end].decode('utf-16-le')
    except UnicodeError as e:raise ValueError('UTF16 source boundary splits a surrogate pair')from e
