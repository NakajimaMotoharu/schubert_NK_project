"""Pure nine-stream cold-current target oracle. No VM or dump authority.

NK-OPS-001/SS343/SS353/SSC254255; PT-DEP-1188001..004.
Selection is not acceptance: generation, normal termination, source/class IDs,
before/after metadata and independent counter union must also be qualified.
"""
import re

UNITS = {'api': 'schubert-nk-api.service', 'web': 'schubert-nk-web.service',
         'inspector': 'schubert-nk-inbox-inspector.service'}
FIXED = ('backup/backup.exec', 'cleanup/cleanup.exec', 'expiry/expiry.exec', 'parent/parent.exec')


def targets(invocations):
    if type(invocations) is not dict or set(invocations) != set(UNITS.values()):
        raise ValueError('complete current native generations required')
    values = list(invocations.values())
    if any(type(v) is not str or re.fullmatch('[0-9a-f]{32}', v) is None or v == '0'*32 for v in values):
        raise ValueError('actual nonempty native generations required')
    if len(set(values)) != len(values):
        raise ValueError('distinct current native generations required')
    paths = list(FIXED)
    for role in ('api', 'web'):
        generation = invocations[UNITS[role]]
        paths += ['ordinary-'+role+'193/'+generation+'.terminal.exec',
                  'root-'+role+'193/'+generation+'.before-exec.exec']
    paths += ['ordinary-inspector196/'+invocations[UNITS['inspector']]+'.terminal.exec']
    return tuple(paths)
