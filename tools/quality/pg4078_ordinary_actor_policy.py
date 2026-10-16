"""SSC287 pre-operation actor identity only. Positive data never grants a signal."""


def identity(status, uid, gid, groups):
    def require(v):
        if v is not True: raise ValueError('fixed ordinary actor identity refused')
    require(type(status) is dict and type(uid) is int and type(gid) is int
            and 0 < uid < 4294967295 and 0 < gid < 4294967295)
    require(type(groups) is list and all(type(v) is int and 0 < v < 4294967295 for v in groups)
            and groups == sorted(set(groups)) and gid in groups)
    for key, expected in [('Uid', [uid] * 4), ('Gid', [gid] * 4), ('Groups', groups)]:
        raw = status.get(key)
        require(type(raw) is str)
        fields = raw.split()
        require(all(v.isascii() and v.isdecimal() and str(int(v)) == v for v in fields))
        require([int(v) for v in fields] == expected)
    require(all(type(status.get(k)) is str and status[k].strip() == '0000000000000000'
                for k in ['CapInh', 'CapPrm', 'CapEff', 'CapBnd', 'CapAmb']))
    require(type(status.get('NoNewPrivs')) is str and status['NoNewPrivs'].strip() == '1')
    return True
