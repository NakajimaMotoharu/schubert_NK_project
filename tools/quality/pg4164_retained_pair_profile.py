"""SSC288 exact98/7 current pair. Pure predicates only, never a signal authorization by itself."""
import re
import stat

JAVA=790010
PYTHON=789928
JVM_FDS={str(n)for n in range(96)}|{'100','128'}
PY_FDS={'0','1','2','3','4','6','7'}
ROOT='/opt/schubert-nk/releases/0.1.0-PG3976'


def require(v):
    if v is not True:raise ValueError('exact retained pair refused')


def stable(old,now,upper_ns,child_terminal=False):
    require(type(old)is dict and type(now)is dict and type(upper_ns)is int and upper_ns>=0)
    pid=old.get('pid');require(pid in (JAVA,PYTHON)and now.get('pid')==pid)
    expected=(14181503,'ed8889ef439ebe28100f5a4d4cee289004c55e9bfb108a7a314c37d25aaf7af2',str(PYTHON),JVM_FDS)if pid==JAVA else(14180650,'c8c952de1cf05574e3fdcf5effc076e4aac73748367f49aac23f6cb6300e9fb6','789926',PY_FDS)
    require(old.get('ticks')==now.get('ticks')==expected[0]and old.get('argvSha256')==now.get('argvSha256')==expected[1])
    for value in [old,now]:
        a=value.get('authority');require(type(a)is dict and a.get('PPid')==expected[2]
          and a.get('Uid','').split()==['0']*4 and a.get('Gid','').split()==['0']*4 and a.get('Groups','').split()==['0']
          and a.get('NoNewPrivs')=='0'and a.get('CapInh')==a.get('CapAmb')=='0000000000000000'
          and a.get('CapPrm')==a.get('CapEff')==a.get('CapBnd')=='000001ffffffffff')
        require(value.get('cgroup')=='0::/user.slice/user-1000.slice/session-921.scope\n')
        children=value.get('children');require(children==([]if pid==JAVA else[JAVA])or pid==PYTHON and child_terminal and children==[])
        require(type(value.get('fds'))is dict and set(value['fds'])==expected[3])
    require(old['authority']==now['authority'])
    for fd in expected[3]:
        before=old['fds'][fd];after=now['fds'][fd]
        require(type(before)is dict and type(after)is dict and set(before)==set(after)=={'target','metadata','fdinfo'})
        require(before['target']==after['target']and before['fdinfo']==after['fdinfo'])
        bm,am=before['metadata'],after['metadata']
        require(type(bm)is list and type(am)is list and len(bm)==len(am)==9 and all(type(n)is int and n>=0 for n in bm+am))
        if before['target']=='/run':
            require(bm[:7]==am[:7]and all(bm[i]<=am[i]<=upper_ns for i in [7,8]))
        else:require(bm==am)
        require(type(after['target'])is str and type(after['fdinfo'])is str and 0<len(after['fdinfo'])<=65536
                and len(re.findall(r'^flags:\s+([0-7]+)$',after['fdinfo'],re.M))==1)
        if pid==JAVA:
            path=after['target'];mode=am[4]
            if fd in {'0','1'}:valid=path.startswith('pipe:[')and stat.S_ISFIFO(mode)
            elif fd=='2':valid=path=='/var/lib/pgpt-s1-preservation/pg4146-complete-signed-owned-recovery-v1-recover/java-stderr.private.log'and mode==stat.S_IFREG|0o600
            elif fd=='3':valid=path=='/opt/jdk-25.0.4/lib/modules'and stat.S_ISREG(mode)
            elif fd=='4':valid=path==ROOT+'/operations/batch.jar'and stat.S_ISREG(mode)
            elif 5<=int(fd)<=45:valid=path.startswith(ROOT+'/operations/lib/')and path.endswith('.jar')and stat.S_ISREG(mode)
            elif 46<=int(fd)<=83:valid=path.startswith(ROOT+'/api/lib/')and path.endswith('.jar')and stat.S_ISREG(mode)
            elif fd=='84':valid=path=='/var/lib/pgpt-s1-preservation/pg4112-canonical-epoch-owned-tools-v1/spotbugs-annotations-4.10.4.jar'and mode==stat.S_IFREG|0o400
            elif fd in {'85','88','86','89'}:valid=path==('/run'if fd in {'86','89'}else'/run/schubert-nk')and mode==stat.S_IFDIR|0o755
            elif fd in {'87','90','91','100','128'}:valid=path=='/run/schubert-nk/'+('startup-admission.lock'if fd in {'100','128'}else'maintenance.lock')and am[2:7]==[0,0,stat.S_IFREG|0o600,1,0]
            elif fd in {'92','93'}:valid=path.startswith('socket:[')and stat.S_ISSOCK(mode)
            else:valid=path==('/dev/random'if fd=='94'else'/dev/urandom')and stat.S_ISCHR(mode)
        else:
            path=after['target'];mode=am[4]
            valid=(path.startswith('pipe:[')and stat.S_ISFIFO(mode)if fd in {'0','1','2','6','7'}else path.startswith('socket:[')and stat.S_ISSOCK(mode)if fd=='3'else path=='/var/lib/pgpt-s1-preservation/pg4146-complete-signed-owned-recovery-v1-recover/java-stderr.private.log'and mode==stat.S_IFREG|0o600)
        require(bool(valid))
    return True
