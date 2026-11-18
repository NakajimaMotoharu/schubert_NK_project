"""Named four-column coverage session, independent of suite/class inventory sizes."""


MAX_JAVA_LONG = '9223372036854775807'


def parse_timestamp(value):
    if not isinstance(value, str) or not value.isascii() or not value.isdecimal():
        raise ValueError('nonnegative decimal timestamps required')
    digits = value.lstrip('0') or '0'
    if len(digits) > len(MAX_JAVA_LONG) or (len(digits) == len(MAX_JAVA_LONG) and digits > MAX_JAVA_LONG):
        raise ValueError('coverage session timestamp outside Java long range')
    return int(digits)


def parse(parts, expected_id):
    if not isinstance(expected_id, str) or not expected_id:
        raise ValueError('nonempty session name required')
    if not isinstance(parts, list) or len(parts) != 4 or parts[:2] != ['SESSION', expected_id]:
        raise ValueError('four exact named session fields required')
    start, end = map(parse_timestamp, parts[2:])
    if start > end:
        raise ValueError('session start must precede end')
    return dict(sessionId=expected_id, startMillis=start, endMillis=end)


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
