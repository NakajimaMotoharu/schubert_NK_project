"""BUG1099/YKT868: preserve the sealed metadata-nine plus SHA schema."""
import re


def matches(expected, metadata, digest):
    if type(expected) is not list or len(expected)!=10:
        return False
    if type(metadata) is not list or len(metadata)!=9:
        return False
    if any(type(x) is not int or x<0 for x in expected[:9]+metadata):
        return False
    if type(expected[9]) is not str or re.fullmatch(r'[0-9a-f]{64}',expected[9]) is None:
        return False
    if type(digest) is not str or re.fullmatch(r'[0-9a-f]{64}',digest) is None:
        return False
    return expected==metadata+[digest]
