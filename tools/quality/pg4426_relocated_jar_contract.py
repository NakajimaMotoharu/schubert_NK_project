"""Exact qualified class relocation, preserving every other ZIP byte contract."""
import hashlib
from pathlib import PurePosixPath
import struct
import zipfile
from pg2428_question_signed_candidate import masked, verify_container


def need(value, why):
    if not value:
        raise ValueError(why)


def records(path):
    """Authenticate all local/central/EOCD bytes, including descriptors and offsets."""
    raw = path.read_bytes(); result = {}
    with zipfile.ZipFile(path) as archive:
        rows = archive.infolist()
        need(rows and not archive.comment and rows[0].header_offset == 0, 'no prefix/comment')
        need(len(rows) == len({r.filename for r in rows}), 'unique complete inventory')
        central = archive.start_dir
        for index, info in enumerate(rows):
            name = info.filename.encode('utf-8' if info.flag_bits & 2048 else 'cp437')
            need(not info.extra and not info.comment and info.flag_bits & ~2056 == 0 and info.compress_type in (0, 8), 'fixed ordinary Jar metadata')
            need(not info.filename.startswith('/') and '..' not in PurePosixPath(info.filename).parts, 'relative canonical Jar name')
            local = info.header_offset
            values = struct.unpack_from('<IHHHHHIIIHH', raw, local)
            signature, version, flags, compression, time, date, crc, packed, size, n, extra = values
            need(signature == 0x04034b50 and version == info.extract_version and flags == info.flag_bits
                 and compression == info.compress_type and n == len(name) and extra == 0, 'exact local header')
            end = local + 30 + n
            need(raw[local + 30:end] == name, 'exact local name')
            limit = rows[index + 1].header_offset if index + 1 < len(rows) else archive.start_dir
            content = raw[end:end + info.compress_size]; tail = raw[end + info.compress_size:limit]
            if flags & 8:
                need((crc, packed, size) == (0, 0, 0), 'streaming local sizes zero')
                descriptor = struct.pack('<III', info.CRC, info.compress_size, info.file_size)
                need(tail in (descriptor, b'PK\x07\x08' + descriptor), 'exact descriptor')
            else:
                need((crc, packed, size) == (info.CRC, info.compress_size, info.file_size) and not tail, 'exact local sizes/no tail')
            header = struct.unpack_from('<IHHHHHHIIIHHHHHII', raw, central)
            sig, creator, extract, cf, cm, ct, cd, cc, cp, cs, cn, ce, co, disk, ia, ea, offset = header
            need((sig, extract, cf, cm, ct, cd, cc, cp, cs, cn, ce, co, disk, ia, ea, offset) ==
                 (0x02014b50, info.extract_version, flags, compression, time, date, info.CRC, info.compress_size,
                  info.file_size, len(name), 0, 0, info.volume, info.internal_attr, info.external_attr, local), 'exact central/local full metadata')
            need(creator == info.create_version + (info.create_system << 8) and raw[central + 46:central + 46 + cn] == name, 'exact creator and central name')
            central += 46 + cn
            payload = archive.read(info)  # independently checks decoded CRC
            need(not info.is_dir() or not payload, 'directory empty')
            result[info.filename] = {'sha256': hashlib.sha256(payload).hexdigest(), 'compressed': content,
                                    'header': masked(raw[local:local + 30], [(10, 14), (14, 30)]),
                                    'metadata': (creator, extract, flags, compression, disk, ia, ea),
                                    'descriptorKind': len(tail)}
        need(raw[central:] == struct.pack('<IHHHHIIH', 0x06054b50, 0, 0, len(rows), len(rows),
                                          central - archive.start_dir, archive.start_dir, 0), 'exact complete EOCD/no trailer')
    return result


def verify_relocated_container(before, after, old_classes, new_classes):
    """Expected class maps come only from independent all-Main qualification."""
    old = records(before); new = records(after)
    need({n: r['sha256'] for n, r in old.items() if n.endswith('.class')} == old_classes
         and {n: r['sha256'] for n, r in new.items() if n.endswith('.class')} == new_classes, 'both exact physical Main maps')
    old_files = {n for n in old if not n.endswith('/')}; new_files = {n for n in new if not n.endswith('/')}
    need(new_files == (old_files - set(old_classes)) | set(new_classes), 'no unregistered resource/artifact added or removed')
    def parents(files):
        return {str(parent) + '/' for name in files for parent in PurePosixPath(name).parents if str(parent) != '.'}
    # Maven Jars contain all required directory records, without unused foreign dirs.
    need({n for n in old if n.endswith('/')} == parents(old_files)
         and {n for n in new if n.endswith('/')} == parents(new_files), 'exact derived directories')
    common = set(old) & set(new)
    need([n for n in old if n in common] == [n for n in new if n in common], 'all common member order preserved')
    for name in common:
        need(old[name]['metadata'] == new[name]['metadata'] and old[name]['header'] == new[name]['header'], 'common metadata unchanged except timestamps/qualified sizes')
        changed = name in new_classes and old_classes.get(name) != new_classes[name]
        if not changed:
            need(old[name]['sha256'] == new[name]['sha256'] and old[name]['compressed'] == new[name]['compressed']
                 and old[name]['descriptorKind'] == new[name]['descriptorKind'], 'unchanged encoded payload and descriptor type')
    for name in set(new) - set(old):
        kind = name.endswith('/')
        templates = [r for n, r in old.items() if n.endswith('/') == kind and (kind or n.endswith('.class'))]
        need(templates and any(new[name]['metadata'] == r['metadata'] and new[name]['header'] == r['header']
                              and new[name]['descriptorKind'] == r['descriptorKind'] for r in templates), 'new qualified member uses existing class/directory encoding only')
    if set(old) == set(new):
        verify_container(before, after, {n for n in new_classes if old_classes.get(n) != new_classes[n]})
    return {'allMembersValidated': True, 'added': sorted(set(new) - set(old)), 'removed': sorted(set(old) - set(new)),
            'physicalClasses': len(new_classes), 'allUnchangedCompressedPayloadsIdentical': True}
