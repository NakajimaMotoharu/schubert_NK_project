"""SSC294 exact metadata-only remaining target. No signal/syscall capability."""
import stat

PYTHON = (815643, 15408795)
RETAINER = (817783, 15666115)


def require(value):
    if value is not True:
        raise ValueError('exact remaining half-handoff owner refused')


def target(pid, ticks):
    require(type(pid) is int and type(ticks) is int and (pid, ticks) in {PYTHON, RETAINER})
    return True


def stable_retainer(old, now):
    require(type(old) is dict and type(now) is dict and old == now)
    require((now.get('pid'), now.get('ticks')) == RETAINER
            and now.get('argvSha256') == 'a9deeaa12bc32f5bf4d7df54a844424f97f0f10811bbaf6546a578058c78988a')
    require(now.get('children') == [] and now.get('cgroup') == '0::/user.slice/user-1000.slice/session-986.scope\n')
    a = now.get('authority', {})
    require(a.get('PPid') == '817781' and a.get('Uid', '').split() == ['0'] * 4
            and a.get('Gid', '').split() == ['0'] * 4 and a.get('Groups', '').split() == ['0']
            and a.get('NoNewPrivs') == '0' and a.get('CapInh') == a.get('CapAmb') == '0000000000000000'
            and all(a.get(key) == '000001ffffffffff' for key in ['CapPrm', 'CapEff', 'CapBnd']))
    fds = now.get('fds', {})
    expected = ['pipe:[13981587]', 'pipe:[13981588]', 'pipe:[13981589]',
                '/usr/lib/x86_64-linux-gnu/libffi.so.8.2.0', 'socket:[13984223]']
    require(set(fds) == {'0', '1', '2', '3', '4'} and [fds[str(n)]['target'] for n in range(5)] == expected)
    for n, fd in fds.items():
        require(set(fd) == {'target', 'metadata', 'fdinfo'} and type(fd['metadata']) is list
                and len(fd['metadata']) == 9 and all(type(v) is int and v >= 0 for v in fd['metadata'])
                and type(fd['fdinfo']) is str and 0 < len(fd['fdinfo']) <= 65536)
        require(stat.S_ISFIFO(fd['metadata'][4]) if n in {'0', '1', '2'}
                else fd['metadata'][4] == stat.S_IFREG | 0o644 if n == '3'
                else fd['metadata'][4] == stat.S_IFSOCK | 0o777)
    return True
