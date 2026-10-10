"""SSC254 all-role cold-native delta oracle. Pure data; no operation authority.

NK-OPS-001/SS343/353; BUG1029/YKT798; PT-DEP-1119001..005.
Existing bytes/metadata are independently retained by the eventual owned scope.
"""
ROOT_ROLES = {'parent','cleanup','expiry','root-api','root-api193','root-web193'}
ACCOUNT_ROLES = {'backup':'schubert-backup','inspector':'schubert-inspector',
                 'ordinary-api193':'schubert-api','ordinary-web193':'schubert-web'}
LEGACY = {'parent','cleanup','expiry','root-api','backup','inspector'}
NEW = {'root-api193','root-web193','ordinary-api193','ordinary-web193'}
RW = {
    'morning': {'parent'}, 'api': {'root-api193','ordinary-api193'},
    'web': {'root-web193','ordinary-web193'}, 'backup': {'backup'},
    'cleanup': {'cleanup'}, 'expiry': set(), 'inspector': set(),
}


def plan(parent, entries, effective_rw, accounts):
    """Return strictly finite missing-role actions; preserve any existing valid role."""
    if type(parent) is not dict or set(parent) != {'kind','uid','gid','mode','acl'}:
        raise ValueError('native parent contract refused')
    if (parent['kind']!='directory' or type(parent['uid']) is not int or
        type(parent['gid']) is not int or parent['uid']!=0 or parent['gid']!=0 or parent['acl']!=[]):
        raise ValueError('native parent identity refused')
    if type(parent['mode']) is not int or parent['mode'] not in (0o711,0o755):
        raise ValueError('native parent mode refused')
    if type(entries) is not dict or not LEGACY <= set(entries) <= LEGACY | NEW:
        raise ValueError('native closed role inventory refused')
    if type(accounts) is not dict or set(accounts)!=set(ACCOUNT_ROLES.values()):
        raise ValueError('native fixed NSS roles refused')
    for value in accounts.values():
        if (type(value) is not tuple or len(value)!=2 or
            any(type(x) is not int or x<=0 for x in value)):
            raise ValueError('native fixed NSS identity refused')
    if type(effective_rw) is not dict or set(effective_rw)!=set(RW):
        raise ValueError('native effective role declarations refused')
    if any(type(v) is not set or v!=RW[k] for k,v in effective_rw.items()):
        raise ValueError('native effective RW declaration drift')
    def owner(role):
        return (0,0) if role in ROOT_ROLES else accounts[ACCOUNT_ROLES[role]]
    for role,value in entries.items():
        if (type(value) is not dict or set(value)!={'kind','uid','gid','mode','acl'} or
            value['kind']!='directory' or type(value['uid']) is not int or
            type(value['gid']) is not int or (value['uid'],value['gid'])!=owner(role) or
            type(value['mode']) is not int or value['mode']!=0o700 or value['acl']!=[]):
            raise ValueError('native existing role invariant refused')
    return {
        'parentModeChange': (0o711,0o755) if parent['mode']==0o711 else None,
        'newOnlyDirectories': [dict(role=r,uid=owner(r)[0],gid=owner(r)[1],mode=0o700)
                               for r in sorted(NEW-set(entries))],
        'preserveExistingRoles': sorted(entries),
        'requiresOwnedTerminalScope': True,
        'nativeAccepted': False,
    }
