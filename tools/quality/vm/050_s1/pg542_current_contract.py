"""Closed signed Unit inventory; readonly diagnosis never confers owner/mutation authority."""
UNITS = frozenset({
    'caddy.service', 'schubert-nk-web.service', 'schubert-nk-api.service',
    'schubert-nk-cleanup.service', 'schubert-nk-inbox-inspector.service',
    'schubert-nk-expiry-cleanup.service', 'schubert-nk-backup.service',
    'artemis.service', 'schubert-nk-morning-controller.service',
    'schubert-nk-bootstrap-admin.service'})


def current_units(values):
    if not isinstance(values, dict) or set(values) != UNITS:
        raise ValueError('current Unit inventory refused')
    for name, row in values.items():
        if not isinstance(row, dict) or row.get('Id') != name or row.get('LoadState') != 'loaded':
            raise ValueError('current Unit inventory refused')
        if row.get('MainPID') != '0' or row.get('ControlPID') != '0' or row.get('Job') != '':
            raise ValueError('current Unit inventory refused')
        if row.get('ActiveState') not in ('inactive', 'failed'):
            raise ValueError('current Unit inventory refused')
    return True
