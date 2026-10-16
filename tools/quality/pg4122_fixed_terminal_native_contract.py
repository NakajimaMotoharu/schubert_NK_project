"""SS343/354 SSC193/194 independent literal oracle; never vendor destfile/append authority."""
import hashlib
from pathlib import PurePosixPath
import re
from pg4086_failed_done_recovery_contract import require

ROOT='/run/schubert-nk/pt-coverage'
ROLES={'schubert-nk-api.service':('API','ordinary-api193'),
       'schubert-nk-web.service':('WEB','ordinary-web193')}


def destination(unit, invocation, argv):
    require(type(unit)is str and unit in ROLES and type(invocation)is str
            and re.fullmatch(r'(?!0{32}$)[0-9a-f]{32}',invocation)is not None)
    require(type(argv)is list and all(type(a)is bytes for a in argv))
    label,directory=ROLES[unit]
    # Independent literal from the approved native profile, not a Production method call.
    expected=('-javaagent:/opt/pgpt-tools-pg390/jacoco-agent.jar='
              'output=none,append=false,dumponexit=false,sessionid='+label+'-'+invocation+'-ordinary').encode('ascii')
    require([a for a in argv if a.startswith(b'-javaagent:')]==[expected])
    return str(PurePosixPath(ROOT)/directory/(invocation+'.terminal.exec'))


def preserved(before, after, exports, completed, identities, read, attributes):
    require(type(before)is dict and type(after)is dict and type(exports)is dict
            and set(exports)==set(ROLES) and set(identities)==set(ROLES))
    require(callable(read)and callable(attributes)and type(completed)in (set,frozenset)
            and completed<=set(ROLES))
    paths=set(exports.values());require(len(paths)==2 and not paths&set(before))
    allowed={exports[u]for u in completed}
    require(set(after)==set(before)|allowed)
    parents={str(PurePosixPath(p).parent)for p in allowed}
    for path,b in before.items():
        a=after[path]
        if path in parents:
            require(a['sha256']is None and b['sha256']is None
                    and a['metadata'][:6]==b['metadata'][:6])
        else:require(a==b)
    for unit in completed:
        path=exports[unit];a=after[path];m=a['metadata'];parent=after[str(PurePosixPath(path).parent)]['metadata']
        require(type(m)is list and len(m)==9 and all(type(v)is int for v in m)
                and m[0]==parent[0]and m[2:6]==[identities[unit]['uid'],identities[unit]['gid'],0o100600,1]
                and 5<=m[6]<=16777216)
        require(attributes(path)==[])
        value=read(path)
        require(type(value)is bytes and len(value)==m[6]and value[:5]==bytes([1,192,192,16,7])
                and hashlib.sha256(value).hexdigest()==a['sha256'])
    return True
