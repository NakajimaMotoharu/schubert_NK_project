"""Unused-candidate archive names/types only. Never current/permit/Unit authority."""
from pathlib import PurePosixPath


def check_members(members, files):
    if not isinstance(files, set) or not files:
        raise ValueError('candidate archive inventory')
    directories = {str(p) for n in files for p in PurePosixPath(n).parents if str(p) != '.'}
    names = set()
    for member in members:
        name = member.name
        if not isinstance(name, str) or not name or '\\' in name \
                or name.startswith('/') or any(p in ('', '.', '..') for p in name.split('/')) \
                or name in names:
            raise ValueError('candidate archive path')
        names.add(name)
        if member.isfile():
            if name not in files: raise ValueError('candidate archive foreign file')
        elif member.isdir():
            if name not in directories: raise ValueError('candidate archive foreign directory')
        else: raise ValueError('candidate archive type')
    if names != files | directories:
        raise ValueError('candidate archive missing member')

