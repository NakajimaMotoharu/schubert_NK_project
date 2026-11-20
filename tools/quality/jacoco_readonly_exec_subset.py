"""Read-only 0x1007 exec decoder. Exact binary names stay bytes throughout validation."""


def validate_modified_utf(encoded):
    """Check canonical DataOutput.writeUTF code units without decoding their values."""
    offset = 0
    while offset < len(encoded):
        lead = encoded[offset]
        offset += 1
        if 0x01 <= lead <= 0x7f:
            continue
        if offset < len(encoded):
            second = encoded[offset]
            if lead == 0xc0 and second == 0x80:
                offset += 1
                continue
            if 0xc2 <= lead <= 0xdf and 0x80 <= second <= 0xbf:
                offset += 1
                continue
            lower = 0xa0 if lead == 0xe0 else 0x80
            if (0xe0 <= lead <= 0xef and lower <= second <= 0xbf
                    and offset + 1 < len(encoded) and 0x80 <= encoded[offset + 1] <= 0xbf):
                offset += 2
                continue
        raise ValueError('invalid modified UTF field')


def decode(raw,wanted):
    if (
        type(raw) is not bytes
        or not isinstance(wanted, set)
        or any(type(name) is not str or not name or not name.isascii() for name in wanted)
    ):
        raise ValueError('immutable bytes and explicit ASCII target names')
    offset = 0

    def take(size):
        nonlocal offset
        if type(size) is not int or size < 0 or offset + size > len(raw):
            raise ValueError('truncated fixed evidence record')
        value = raw[offset:offset + size]
        offset += size
        return value

    def number(size):
        return int.from_bytes(take(size),'big')

    def utf_bytes():
        encoded = take(number(2))
        validate_modified_utf(encoded)
        return encoded

    def varint():
        value = 0
        for shift in range(0,35,7):
            byte = number(1)
            value |= (byte & 127) << shift
            if not byte & 128:
                if value > 0x7fffffff:
                    raise ValueError('nonnegative Java int count required')
                if shift and byte == 0:
                    raise ValueError('nonminimal compact count')
                return value
        raise ValueError('overlong compact integer')

    if take(5) != bytes.fromhex('01c0c01007'):
        raise ValueError('pinned exec header required')
    wanted_bytes = {n.encode('ascii'):n for n in wanted}
    found,sessions,identities = {},[],set()
    binary_names = set()
    records = 0
    while offset < len(raw):
        tag = number(1)
        if tag == 0x10:
            label = utf_bytes()
            start = int.from_bytes(take(8), 'big', signed=True)
            end = int.from_bytes(take(8), 'big', signed=True)
            if sessions or not 0 <= start <= end:
                raise ValueError('one ordered original session only')
            sessions.append(dict(labelBytesHex=label.hex(),startMillis=start,endMillis=end))
        elif tag == 0x11:
            identity,name = number(8),utf_bytes()
            if identity in identities:
                raise ValueError('no duplicate class record union')
            identities.add(identity)
            count = varint()
            packed = take((count + 7) // 8)
            final_bits = count % 8
            if final_bits and packed[-1] >> final_bits:
                raise ValueError('nonzero final probe padding')
            if name in binary_names:
                if name in wanted_bytes:
                    raise ValueError('one target class identity only')
                raise ValueError('no duplicate original binary name')
            binary_names.add(name)
            records += 1
            if name in wanted_bytes:
                key = wanted_bytes[name]
                hit = [i for i in range(count) if packed[i // 8] & (1 << (i % 8))]
                found[key] = dict(crc64=format(identity,'x'),probeCount=count,hitProbeIds=hit,
                    missedProbeIds=[i for i in range(count) if not packed[i // 8] & (1 << (i % 8))])
        else:
            raise ValueError('unexpected exec record, no appended header or unknown block')
    if len(sessions) != 1 or set(found) != wanted:
        raise ValueError('one session and all exact target records required')
    return dict(classes=found,sessions=sessions,totalClassRecords=records)


def selftest():
    header = bytes.fromhex('01c0c01007')
    session = b'\x10\x00\x03RUN' + (1).to_bytes(8,'big') + (2).to_bytes(8,'big')
    record = b'\x11' + (1).to_bytes(8,'big') + b'\x00\x01X\x03\x05'
    good = header + session + record
    parsed = decode(good,{'X'})
    assert parsed['classes']['X'] == dict(crc64='1',probeCount=3,hitProbeIds=[0,2],missedProbeIds=[1])
    assert parsed['totalClassRecords'] == 1 and parsed['sessions'][0]['startMillis'] == 1
    long_record = record[:-2] + b'\x80\x01' + b'\x00'*16
    assert decode(header + session + long_record,{'X'})['classes']['X']['probeCount'] == 128
    fixtures = [b'',b'\x00' + good[1:],header[:-1] + b'\x08' + good[5:],good + b'\x99',
        good[:-1],good + record,good + session,header + session + record[:-2] + b'\x80'*6,
        header + session[:-16] + (3).to_bytes(8,'big') + (2).to_bytes(8,'big') + record,
        good + header]
    for bad in fixtures:
        try:
            decode(bad,{'X'})
        except ValueError:
            continue
        raise AssertionError('malformed exec metadata fixture accepted')
    return 12
