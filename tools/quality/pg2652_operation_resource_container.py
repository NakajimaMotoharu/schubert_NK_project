"""Exact approved four changed templates/one added script; no unknown JAR delta."""
import hashlib
import struct
import zipfile

CHANGED = {
    'templates/admin/user-detail.html': ('659c9e6b0cc083c40a675a086ab7c9fd75a17378ea7be58b94b5ed9619eaa569', 'c74fe2ced5c6492369f243bf9930e52e88fef40b18492195a1ac01a9b05f8fba'),
    'templates/admin/user-new.html': ('98583e3b92f93b2211884044a0ba5f26628f826c55d35fbfcad7b01b06de5bbd', '97fd0f78dbfbe4538ca36e5ddda507ed55d762c040d12b09d544fc568b0dbedd'),
    'templates/notifications/detail.html': ('d367ae916c4ba0d21ebaf0050f8e34b2365c6d5c5ce1a38f26687977b04041e0', '10e4f709e65f4da0ee7f6afe05c13b3cc21cb3a0ad497a52ba1a2a2408824701'),
    'templates/questions/detail.html': ('6e41db2b0c0a7ade2814160ad3f91df880b9a7dd1a5790b29dae8f6e2e1899fb', '106063b219b894417619b35cd8a120cffc4f4aa21432f59bfcf6b54f7595e9f2')}
ADDED = {'static/js/operation-post-submit.js': '771029cb5f80dd32d17af01a5fb8e7fe471a615268de6645d543f57001050429'}


def require(value):
    if not value:
        raise ValueError('exact approved new-resource container refused')


def masked(raw, ranges):
    result = bytearray(raw)
    for a, b in ranges:
        result[a:b] = bytes(b-a)
    return bytes(result)


def records(path):
    raw = path.read_bytes()
    with zipfile.ZipFile(path) as jar:
        rows = jar.infolist(); names = [x.filename for x in rows]
        require(rows and len(names) == len(set(names)) and rows[0].header_offset == 0 and not jar.comment)
        result = {}; offset = jar.start_dir
        for index, info in enumerate(rows):
            start = info.header_offset; require(raw[start:start+4] == b'PK\x03\x04')
            n, e = struct.unpack_from('<HH', raw, start+26); header_end = start+30+n+e
            limit = rows[index+1].header_offset if index+1 < len(rows) else jar.start_dir
            header = raw[start:header_end]; compressed = raw[header_end:header_end+info.compress_size]
            tail = raw[header_end+info.compress_size:limit]
            if info.flag_bits & 8:
                descriptor = struct.pack('<III', info.CRC, info.compress_size, info.file_size)
                require(tail in (descriptor, b'PK\x07\x08'+descriptor))
            else:
                require(not tail)
            require(raw[offset:offset+4] == b'PK\x01\x02')
            cn, ce, cc = struct.unpack_from('<HHH', raw, offset+28); end = offset+46+cn+ce+cc
            require(not info.extra and not info.comment and not(info.flag_bits & 1))
            require(raw[start+30:start+30+n].decode('utf-8') == info.filename)
            require(raw[offset+46:offset+46+cn].decode('utf-8') == info.filename)
            result[info.filename] = {
                'sha': hashlib.sha256(jar.read(info)).hexdigest(), 'local': header,
                'compressed': compressed, 'descriptor': tail, 'central': raw[offset:end],
                'metadata': tuple(getattr(info, x) for x in ('compress_type','create_system','create_version','extract_version','flag_bits','volume','internal_attr','external_attr','extra','comment'))}
            offset = end
        tail = raw[offset:]; require(len(tail) == 22 and tail[:4] == b'PK\x05\x06')
        require(struct.unpack_from('<I',tail,12)[0] == offset-jar.start_dir and struct.unpack_from('<I',tail,16)[0] == jar.start_dir)
        require(struct.unpack_from('<H', tail, 8)[0] == len(rows) and struct.unpack_from('<H',tail,10)[0] == len(rows))
        return names, result, tail


def verify(before, after, changed=None, added=None):
    changed = CHANGED if changed is None else changed
    added = ADDED if added is None else added
    old_names, a, old_tail = records(before); new_names, b, new_tail = records(after)
    require(set(b)-set(a) == set(added) and not set(a)-set(b))
    require([n for n in new_names if n not in added] == old_names)
    require({n for n in a if a[n]['sha'] != b[n]['sha']} == set(changed))
    for name, (old, new) in changed.items():
        require(a[name]['sha'] == old and b[name]['sha'] == new)
    for name, expected in added.items():
        require(b[name]['sha'] == expected and not name.endswith('.class'))
        require(b[name]['metadata'] == a[next(n for n in old_names if not n.endswith('/'))]['metadata'])
    for name in a:
        x, y = a[name], b[name]; require(x['metadata'] == y['metadata'])
        require(masked(x['local'], [(10,14)]+([(14,26)] if name in changed else [])) == masked(y['local'], [(10,14)]+([(14,26)] if name in changed else [])))
        require(masked(x['central'], [(12,16),(42,46)]+([(16,28)] if name in changed else [])) == masked(y['central'], [(12,16),(42,46)]+([(16,28)] if name in changed else [])))
        if name not in changed:
            require((x['compressed'],x['descriptor']) == (y['compressed'],y['descriptor']))
    # Central size/offset and both entry counts change only because one exact new member exists.
    require(masked(old_tail, [(8,20)]) == masked(new_tail, [(8,20)]))
    return {'changedResources': len(changed), 'addedResources': len(added), 'MainChanged': 0}
