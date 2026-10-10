"""SSC257 exact current Expiry dependency transition; no generic terminal ignore."""
from pg1133_fixed_broker_policy import stopped

EXPIRY = 'schubert-nk-expiry-cleanup.service'
BROKER = 'artemis.service'
CLEANUP = 'schubert-nk-cleanup.service'
REQUIRES = {'postgresql.service', 'artemis.service', 'sysinit.target', 'system.slice', '-.mount'}
TEN = {BROKER, EXPIRY, CLEANUP, 'caddy.service', 'schubert-nk-api.service', 'schubert-nk-web.service',
       'schubert-nk-backup.service', 'schubert-nk-bootstrap-admin.service',
       'schubert-nk-inbox-inspector.service', 'schubert-nk-morning-controller.service'}


def require(ok):
    if not ok: raise ValueError('fixed dependent oneshot transition refused')


def expiry(before, after, dependencies):
    require(type(before) is dict and type(after) is dict and set(before) == set(after))
    require(before['Id'] == EXPIRY and before['InvocationID'] == 'e8bb5cda8e5044d8a541fbe2bbf0f725' and
            before['Type'] == 'oneshot' and before['RemainAfterExit'] == 'yes' and
            before['ActiveState'] == 'active' and before['SubState'] == 'exited' and
            before['MainPID'] == before['ControlPID'] == '0' and before['Job'] == '' and
            before['Result'] == 'success' and before['ExecMainCode'] == '1' and before['ExecMainStatus'] == '0' and
            before['ExecMainStartTimestampMonotonic'] == '34900018429' and
            before['ExecMainExitTimestampMonotonic'] == '35016395225')
    require(type(dependencies) is dict and set(dependencies) == {'Requires', 'BindsTo', 'PartOf'} and
            dependencies['BindsTo'] == dependencies['PartOf'] == '' and type(dependencies['Requires']) is str)
    values = dependencies['Requires'].split()
    require(len(values) == len(set(values)) and set(values) == REQUIRES)
    require(after['ActiveState'] == 'inactive' and after['SubState'] == 'dead')
    require(all(before[key] == after[key] for key in before.keys() - {'ActiveState', 'SubState'}))
    return True


def whole(before, after, dependencies, cleanup_active=False):
    require(type(before) is dict and type(after) is dict and set(before) == set(after) == TEN and type(cleanup_active) is bool)
    require(EXPIRY in before and BROKER in before)
    for name in before:
        a, b = before[name], after[name]
        if name == BROKER: stopped(a, b)
        elif name == EXPIRY: expiry(a, b, dependencies)
        else: require(a == b)
        activated_cleanup = (cleanup_active and name == CLEANUP and a == b and b['Type'] == 'oneshot' and
                             b['RemainAfterExit'] == 'yes' and b['ActiveState'] == 'active' and b['SubState'] == 'exited' and
                             b['InvocationID'] == '48281323ca3743cbbaddd706e0c4edc5' and
                             b['ExecMainStartTimestampMonotonic'] == '34688004646' and
                             b['ExecMainExitTimestampMonotonic'] == '34751080043' and
                             b['ExecMainCode'] == '1' and b['ExecMainStatus'] == '0')
        require(b['MainPID'] == b['ControlPID'] == '0' and b['Job'] == '' and
                (b['ActiveState'] in ('inactive', 'failed') or activated_cleanup))
    return True
