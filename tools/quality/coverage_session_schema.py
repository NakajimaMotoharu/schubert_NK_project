"""Named four-column coverage session, independent of suite/class inventory sizes."""


def parse(parts, expected_id):
    if not isinstance(parts,list) or len(parts) != 4 or parts[:2] != ['SESSION',expected_id]:
        raise ValueError('four exact named session fields required')
    if any(not isinstance(v,str) or not v.isascii() or not v.isdecimal() for v in parts[2:]):
        raise ValueError('nonnegative decimal timestamps required')
    start, end = map(int,parts[2:])
    if start > end:
        raise ValueError('session start must precede end')
    return dict(sessionId=expected_id,startMillis=start,endMillis=end)


def selftest():
    assert parse(['SESSION','fixture','1','2'],'fixture') == dict(sessionId='fixture',startMillis=1,endMillis=2)
    vectors = [
        ['SESSION','fixture','1'],['SESSION','fixture','1','2','3'],
        ['SESSION','fixture','2','1'],['SESSION','other','1','2'],
        ['SESSION','fixture','-1','2'],['SESSION','fixture','x','2']]
    for value in vectors:
        try:
            parse(value,'fixture')
        except ValueError:
            continue
        raise AssertionError('malformed session accepted')
    return 1 + len(vectors)
