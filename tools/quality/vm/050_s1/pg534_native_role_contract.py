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
UNITS = frozenset(('caddy.service', 'schubert-nk-web.service', 'schubert-nk-api.service',
                   'schubert-nk-cleanup.service', 'schubert-nk-inbox-inspector.service',
                   'schubert-nk-expiry-cleanup.service', 'schubert-nk-backup.service',
                   'artemis.service', 'schubert-nk-morning-controller.service',
                   'schubert-nk-bootstrap-admin.service'))


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


def terminal_units(units):
    """Declaration/idle planning check only; no PID1 receipt/actor/runtime authorization."""
    require(isinstance(units, dict) and set(units) == UNITS)
    for unit, user, remain, expected_codes in (
            ('schubert-nk-bootstrap-admin.service', 'schubert-api', 'no', {'20'}),
            ('schubert-nk-inbox-inspector.service', 'schubert-inbox-inspector', 'yes', {'10'})):
        row = units[unit]
        fields = {'Id', 'LoadState', 'User', 'Group', 'Type', 'Restart', 'RemainAfterExit',
                  'MainPID', 'ControlPID', 'Job', 'SuccessExitStatus', 'KillMode',
                  'SendSIGKILL', 'ExecStart'}
        require(isinstance(row, dict) and fields <= set(row)
                and all(isinstance(row[k], str) for k in fields))
        require(isinstance(row, dict) and row['Id'] == unit and row['LoadState'] == 'loaded'
                and row['User'] == row['Group'] == user and row['Type'] == 'oneshot'
                and row['Restart'] == 'no' and row['RemainAfterExit'] == remain
                and row['MainPID'] == row['ControlPID'] == '0' and row['Job'] == '')
        require(isinstance(row['SuccessExitStatus'], str)
                and set(row['SuccessExitStatus'].split()) == expected_codes)
        require(row['KillMode'] == 'control-group' and row['SendSIGKILL'] == 'no')
        entry = row['ExecStart']
        require(isinstance(entry, str))
        if unit == 'schubert-nk-bootstrap-admin.service':
            require('dev.codex.schubert.nk.api.bootstrap.BootstrapAdminMain' in entry
                    and 'BOOTSTRAP-' in entry and '-ordinary' in entry
                    and 'RootStartupMain' not in entry)
        else:
            require('/opt/schubert-nk/current/operations/bin/schubert-nk-inbox-inspector' in entry)
    return {'terminalUnitsDeclared': 2, 'metadataOnly': True, 'startupAuthorized': False}
