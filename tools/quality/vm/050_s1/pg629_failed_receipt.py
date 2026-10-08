"""SSC228 fixed genuine PID1 failure data; no owner or operation authority."""

BOOT = 'cc9ed8747f4f450ea1888de1e42c8441'
INV = '3a2de24f931544c0a2fd83556a659cd0'
START = 97060184910
END = 97094171993


def failed30(rows):
    def require(value):
        if not value:
            raise ValueError('fixed failed30 receipt rejected')
    require(type(rows) is list and len(rows) == 5)
    stamps, cursors = [], set()
    for row in rows:
        require(type(row) is dict)
        require(all(row.get(k) == v and type(row.get(k)) is str for k, v in {
            '_BOOT_ID': BOOT, '_PID': '1', '_UID': '0', '_COMM': 'systemd',
            'UNIT': 'schubert-nk-morning-controller.service', 'INVOCATION_ID': INV,
        }.items()))
        stamp, cursor = row.get('__MONOTONIC_TIMESTAMP'), row.get('__CURSOR')
        require(type(stamp) is str and stamp.isascii() and stamp.isdigit())
        require(START <= int(stamp) <= START + 1800000000)
        require(type(cursor) is str and bool(cursor) and cursor not in cursors)
        stamps.append(int(stamp)); cursors.add(cursor)
    require(stamps == sorted(stamps) and len(set(stamps)) == 5)
    expected = [
        ('7d4958e842da4a758f6c1cdc7b36dcc5', 97060187042,
         {'JOB_ID': '98394', 'JOB_TYPE': 'start'}),
        ('98e322203f7a4ed290d09fe03c09fe15', 97094172037,
         {'EXIT_CODE': 'exited', 'EXIT_STATUS': '30'}),
        ('d9b373ed55a64feb8242e02dbe79a49c', 97094172347, {}),
        ('be02cf6855d2428ba40df7e9d022f03d', 97094172397,
         {'JOB_ID': '98394', 'JOB_TYPE': 'start', 'JOB_RESULT': 'failed'}),
        ('ae8f7b866b0347b9af31fe1c80b127c0', 97094172443, {}),
    ]
    for row, (message, stamp, fields) in zip(rows, expected):
        require(row.get('MESSAGE_ID') == message and int(row['__MONOTONIC_TIMESTAMP']) == stamp)
        require(all(row.get(k) == v and type(row.get(k)) is str for k, v in fields.items()))
    return {'startMonotonicUs': START, 'endMonotonicUs': END,
            'status': 30, 'elapsedSeconds': (END - START) / 1000000,
            'oldScopesNormalized': False}
