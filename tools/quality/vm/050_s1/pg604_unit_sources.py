"""BUG885/YKT654 fixed current ten Unit fragments + eight existing drop-ins only."""
UNITS=('caddy.service','schubert-nk-web.service','schubert-nk-api.service','schubert-nk-cleanup.service','schubert-nk-inbox-inspector.service','schubert-nk-expiry-cleanup.service','schubert-nk-backup.service','artemis.service','schubert-nk-morning-controller.service','schubert-nk-bootstrap-admin.service')
DROPS={
    'caddy.service':('schubert-nk-startup-policy.conf',),
    'schubert-nk-web.service':('zz-pg471-native193.conf',),
    'schubert-nk-api.service':('pg406-root-coverage.conf','zz-pg471-native193.conf'),
    'schubert-nk-cleanup.service':('pg390-native-coverage.conf',),
    'schubert-nk-expiry-cleanup.service':('pg394-native-coverage.conf',),
    'schubert-nk-backup.service':('pg390-native-coverage.conf',),
    'schubert-nk-morning-controller.service':('pg477-native-coverage.conf',)}


def sources(rows):
    if not isinstance(rows,dict)or set(rows)!=set(UNITS):raise ValueError('fixed Unit sources required')
    result=set()
    for unit in UNITS:
        value=rows[unit]
        if not isinstance(value,dict)or set(value)!={'FragmentPath','DropInPaths'}:
            raise ValueError('fixed Unit source fields required')
        fragment='/usr/lib/systemd/system/caddy.service'if unit=='caddy.service'else'/etc/systemd/system/'+unit
        expected={'/etc/systemd/system/'+unit+'.d/'+n for n in DROPS.get(unit,())}
        raw=value['DropInPaths']
        if not isinstance(raw,str)or value['FragmentPath']!=fragment:
            raise ValueError('fixed Unit source profile required')
        actual=raw.split()
        if len(actual)!=len(set(actual))or set(actual)!=expected:
            raise ValueError('fixed Unit drop-in profile required')
        result.add(fragment);result.update(expected)
    if len(result)!=18:raise ValueError('fixed Unit source inventory required')
    return tuple(sorted(result))
