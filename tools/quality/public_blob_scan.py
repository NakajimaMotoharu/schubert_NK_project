"""Allowlisted Gitleaks findings for an explicit, regularized Git-blob snapshot only."""
import hashlib
import json
from pathlib import PurePosixPath
import re


def sha(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(name):
    path = PurePosixPath(name)
    if not name or path.is_absolute() or '..' in path.parts or str(path) != name:
        raise ValueError('invalid public blob path')
    if any(ord(char) < 32 or ord(char) == 127 for char in name):
        raise ValueError('control character in public blob path')
    return name


def sanitize(raw, known, root):
    """Never copy Secret, Match, Description, Author, Fingerprint, or unknown fields."""
    values = json.loads(raw)
    if values is None:
        values = []
    if not isinstance(values, list):
        raise ValueError('finding array required')
    output = []
    for row in values:
        if not isinstance(row, dict):
            raise ValueError('finding object required')
        rule = row.get('RuleID')
        if not isinstance(rule, str) or not re.fullmatch(r'[a-z0-9][a-z0-9-]{0,100}', rule):
            raise ValueError('known rule identifier shape required')
        name = row.get('File')
        if not isinstance(name, str):
            raise ValueError('public file binding required')
        prefix = str(root) + '/'
        if name.startswith(prefix):
            name = name[len(prefix):]
        safe_path(name)
        if name not in known:
            raise ValueError('unknown file binding')
        start, end = row.get('StartLine'), row.get('EndLine')
        if type(start) is not int or type(end) is not int or not 1 <= start <= end <= known[name]['lines']:
            raise ValueError('finding line binding required')
        output.append(dict(ruleId=rule, path=name, startLine=start, endLine=end,
                           inputSha256=known[name]['sha256']))
    return output
