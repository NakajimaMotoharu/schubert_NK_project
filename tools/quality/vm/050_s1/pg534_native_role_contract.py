"""BUG827/YKT596 closed native namespace metadata; never grants capture/actor/source acceptance."""
import re

# Literal SS343/SSC193196 mapping, not inferred from optional directory presence.
CURRENT = {
    'parent': ('schubert-nk-morning-controller.service', 0, 0, 'parent.exec'),
    'backup': ('schubert-nk-backup.service', 992, 977, 'backup.exec'),
    'cleanup': ('schubert-nk-cleanup.service', 0, 0, 'cleanup.exec'),
    'expiry': ('schubert-nk-expiry-cleanup.service', 0, 0, 'expiry.exec'),
    'root-api193': ('schubert-nk-api.service', 0, 0, 'before-exec.exec'),
    'root-web193': ('schubert-nk-web.service', 0, 0, 'before-exec.exec'),
    'ordinary-api193': ('schubert-nk-api.service', 999, 981, 'terminal.exec'),
    'ordinary-web193': ('schubert-nk-web.service', 997, 980, 'terminal.exec'),
    'ordinary-inspector196': ('schubert-nk-inbox-inspector.service', 991, 976, 'terminal.exec'),
    'ordinary-bootstrap196': ('schubert-nk-bootstrap-admin.service', 999, 981, 'terminal.exec'),
}
HISTORICAL = frozenset(('ordinary-web', 'ordinary-api', 'inspector', 'root-web', 'root-api'))


def require(value):
    if not value:
        raise ValueError('fixed native role metadata unavailable')


def classify(present):
    require(isinstance(present, (tuple, list)) and all(isinstance(r, str) for r in present))
    require(len(present) == len(set(present)) and set(present) <= set(CURRENT))
    return {'present': sorted(present), 'missing': sorted(set(CURRENT) - set(present)),
            'requiredRoles': sorted(CURRENT), 'roleMetadataOnly': True,
            'nativeAccepted': False, 'coverageAccepted': False}


def inventory(native):
    require(isinstance(native, dict) and set(native) == set(CURRENT) | HISTORICAL)
    present = []
    for role, (_, uid, gid, suffix) in CURRENT.items():
        rows = native[role]
        require(isinstance(rows, list) and len(rows) <= 1)
        for row in rows:
            require(isinstance(row, dict)
                    and set(row) == {'name', 'size', 'uid', 'gid', 'mode'})
            name = row['name']
            require(isinstance(name, str))
            require(name == suffix if role in ('parent', 'backup', 'cleanup', 'expiry') else
                    re.fullmatch(r'(?!0{32}\.)[0-9a-f]{32}\.' + re.escape(suffix), name) is not None)
            require(all(type(row[k]) is int for k in ('size', 'uid', 'gid', 'mode')))
            require(0 < row['size'] <= 16777216 and row['uid'] == uid and row['gid'] == gid
                    and row['mode'] == 0o100600)
            present.append(role)
    # Historical paths stay preserved; their contents never become current native streams.
    for role in HISTORICAL:
        require(isinstance(native[role], list))
    return classify(present)
