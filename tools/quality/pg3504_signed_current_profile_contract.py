"""SSC285 pure complete39-FD profile, no process/DB/signal operations."""
import re
import stat

FDS = {str(n) for n in range(37)} | {'43', '128'}
ROOT = '/opt/schubert-nk/releases/0.1.0-PG3420'
AUTHORITY = {'Uid', 'Gid', 'Groups', 'CapInh', 'CapPrm', 'CapEff', 'CapBnd', 'CapAmb',
             'NoNewPrivs', 'Seccomp', 'Umask'}


def canonical_actor(value):
    keys = {'pid', 'ppid', 'ticks', 'argvSha256', 'argv', 'exe', 'status', 'root', 'cgroup', 'fds', 'children'}
    if type(value) is not dict or set(value) != keys or type(value['status']) is not str:
        raise ValueError('complete actual actor shape required')
    fields = dict(line.split(':', 1) for line in value['status'].splitlines() if ':' in line)
    if not AUTHORITY <= fields.keys():
        raise ValueError('complete process authority required')
    authority = {k: fields[k].strip() for k in AUTHORITY}
    if authority['Uid'].split() != ['0'] * 4 or authority['Gid'].split() != ['0'] * 4:
        raise ValueError('actual root authority required')
    return {**{k: v for k, v in value.items() if k != 'status'}, 'authority': authority}


def flags(raw):
    values = re.findall(r'^flags:\s+([0-7]+)$', raw, re.M)
    if len(values) != 1:
        raise ValueError('one complete fd flag field required')
    return int(values[0], 8)


def fresh39(old, current, upper_ns):
    a, b = canonical_actor(old), canonical_actor(current)
    if type(upper_ns) is not int or upper_ns < 0 or any(a[k] != b[k] for k in a.keys() - {'fds'}):
        raise ValueError('same full authority/identity required')
    if (a['pid'] != 410196 or a['ticks'] != 8469964 or a['ppid'] != 410194
            or a['argvSha256'] != '7da390fc72f2f1fa5ceaa6fdb5c797e1dea89f20409f10dfa2f3b831f92036e3'
            or a['root'] != '/' or a['exe'] != '/opt/jdk-25.0.4/bin/java' or a['children']):
        raise ValueError('only actual fixed signed-current failed actor')
    if type(a['fds']) is not dict or set(a['fds']) != FDS or set(b['fds']) != FDS:
        raise ValueError('all39 exact descriptor set required')
    for n, x in a['fds'].items():
        y = b['fds'][n]
        for v in [x, y]:
            if type(v) is not dict or set(v) != {'target', 'metadata', 'fdinfo'}:
                raise ValueError('complete descriptor fields required')
            if (type(v['target']) is not str or type(v['fdinfo']) is not str
                    or type(v['metadata']) is not list or len(v['metadata']) != 9
                    or any(type(z) is not int or z < 0 for z in v['metadata'])):
                raise ValueError('complete typed descriptor metadata required')
        if x['target'] != y['target'] or x['fdinfo'] != y['fdinfo']:
            raise ValueError('same target/complete fdinfo required')
        if n in {'29', '32'}:
            if (x['target'] != '/run' or x['metadata'][:7] != y['metadata'][:7]
                    or any(not x['metadata'][i] <= y['metadata'][i] <= upper_ns for i in [7, 8])):
                raise ValueError('only bounded shared run chrono may advance')
        elif x != y:
            raise ValueError('all other37 descriptors must remain exact')
        expected_flags = (0 if n == '0' else 1 if n in {'1', '2'} else 0o2700000 if n in {'28', '29', '31', '32'}
                          else 0o12400000 if n in {'30', '33'} else 0o2100000 if n in {'34', '43', '128'} else 0o100000)
        if flags(y['fdinfo']) != expected_flags:
            raise ValueError('fixed access flags required')
        target = y['target']; mode = y['metadata'][4]
        if n in {'0', '1', '2'}:
            good = target.startswith('pipe:[') and stat.S_ISFIFO(mode)
        elif n == '3':
            good = target == '/opt/jdk-25.0.4/lib/modules' and stat.S_ISREG(mode)
        elif n == '4':
            good = target == ROOT + '/operations/batch.jar' and stat.S_ISREG(mode)
        elif n in {str(i) for i in range(5, 28)}:
            good = target.startswith(ROOT + '/operations/lib/') and target.endswith('.jar') and stat.S_ISREG(mode)
        elif n in {'28', '31', '29', '32'}:
            good = target == ('/run' if n in {'29', '32'} else '/run/schubert-nk') and mode == stat.S_IFDIR | 0o755
        elif n in {'30', '33', '34', '43', '128'}:
            good = target == '/run/schubert-nk/' + ('startup-admission.lock' if n in {'43', '128'} else 'maintenance.lock') and mode == stat.S_IFREG | 0o600 and y['metadata'][2:4] == [0, 0] and y['metadata'][5:7] == [1, 0]
        else:
            good = target == ('/dev/random' if n == '35' else '/dev/urandom') and stat.S_ISCHR(mode)
        if not good:
            raise ValueError('fixed descriptor semantic target required')
    if b['fds']['29'] != b['fds']['32']:
        raise ValueError('both run descriptors must be identical fresh linked object')
    return True
