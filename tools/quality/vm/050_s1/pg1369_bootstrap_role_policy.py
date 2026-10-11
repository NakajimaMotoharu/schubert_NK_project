"""SSC263 independent one-role filesystem delta, never execution authority.

NK-OPS-001/N11; SS343/353; BUG1088/YKT857; PT-OPS-ROLE1369001..004.
No runtime/JDBC/Unit operations and no production-generated expected values.
"""
import re
import stat

ROOT='/run/schubert-nk/pt-coverage'
ROLE='ordinary-bootstrap196'
OLD_ROLES=frozenset(('backup','cleanup','expiry','inspector','parent','root-api',
    'root-api193','root-web193','ordinary-api193','ordinary-web193','ordinary-inspector196'))

def require(value):
    if not value:raise ValueError('fixed one-role delta refused')

def entry(value):
    require(type(value)is dict and set(value)=={'metadata','sha256'})
    m=value['metadata'];h=value['sha256']
    require(type(m)is list and len(m)==9 and all(type(x)is int for x in m)
            and m[0]>0 and m[1]>0 and m[6]>=0)
    require(h is None or type(h)is str and re.fullmatch('[0-9a-f]{64}',h)is not None)
    return m

def before_valid(value):
    require(type(value)is dict and ROOT in value and ROOT+'/'+ROLE not in value)
    for p,e in value.items():
        require(type(p)is str and (p==ROOT or p.startswith(ROOT+'/')))
        entry(e)
    m=entry(value[ROOT]);require(m[2:5]==[0,0,stat.S_IFDIR|0o755]and m[5]==13 and m[6]==260 and value[ROOT]['sha256']is None)
    directories={p[len(ROOT)+1:]for p,e in value.items()if p!=ROOT and stat.S_ISDIR(e['metadata'][4])}
    require(directories==OLD_ROLES)
    require(len(value)==30 and sum(stat.S_ISREG(e['metadata'][4])for e in value.values())==18)
    return True

def delta(before,after,start_ns,end_ns):
    before_valid(before)
    require(type(after)is dict and set(after)==set(before)|{ROOT+'/'+ROLE})
    require(type(start_ns)is int and type(end_ns)is int and 0<start_ns<=end_ns)
    for p,e in after.items():entry(e)
    require(all(after[p]==v for p,v in before.items()if p!=ROOT))
    a=entry(after[ROOT]);b=entry(before[ROOT])
    require(a[:5]==b[:5]and a[5]==b[5]+1 and a[6]==b[6]+20
            and all(start_ns<=x<=end_ns for x in a[7:]) and after[ROOT]['sha256']is None)
    c=entry(after[ROOT+'/'+ROLE])
    require(c[0]==b[0]and c[1]not in {v['metadata'][1]for v in before.values()if v['metadata'][0]==c[0]}
            and c[2:7]==[999,981,stat.S_IFDIR|0o700,2,40]
            and all(start_ns<=x<=end_ns for x in c[7:])and after[ROOT+'/'+ROLE]['sha256']is None)
    return True
