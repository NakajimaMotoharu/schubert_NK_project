"""Read-only proof of the current owned localhost-only CHR SOCKS listener.

BUG1050/YKT819; SS355; PT-DEP-1191001..003. No start, signal or VM operation.
"""
import hashlib
from pathlib import Path

EXPECTED = {'pid':401093,'ticks':5513311,'argvSha256':'e0ec1bc2ff2373f4702a2ab31ef7df6da5c164288db178e17f11661c3676bf6a',
            'executable':'/usr/bin/ssh','ppid':4192,'uids':(1000,1000,1000,1000),
            'gids':(1000,1000,1000,1000),'listenerAddresses':('0100007F:D781',)}


def qualify(observed):
    if type(observed) is not dict or set(observed) != set(EXPECTED):
        raise ValueError('current owned SOCKS schema refused')
    if any(type(observed[k]) is not type(v) or observed[k] != v for k,v in EXPECTED.items()):
        raise ValueError('current owned loopback SOCKS refused')
    for key in ('uids','gids'):
        if any(type(x) is not int for x in observed[key]):raise ValueError('SOCKS numeric identity refused')
    return dict(observed)


def capture():
    p = Path('/proc')/str(EXPECTED['pid'])
    try:
        before = (p/'stat').read_text().rpartition(')')[2].split()
        argv = (p/'cmdline').read_bytes()
        status = dict(line.split(':',1) for line in (p/'status').read_text().splitlines() if ':' in line)
        sockets = set()
        for fd in (p/'fd').iterdir():
            target = str(fd.readlink())
            if target.startswith('socket:['):sockets.add(target[8:-1])
        listeners = []
        for table in ('tcp','tcp6'):
            for line in (p/'net'/table).read_text().splitlines()[1:]:
                fields = line.split()
                if len(fields)>=10 and fields[3]=='0A' and fields[9] in sockets:
                    listeners.append(fields[1])
        observed = {'pid':EXPECTED['pid'],'ticks':int(before[19]),'argvSha256':hashlib.sha256(argv).hexdigest(),
                    'executable':str((p/'exe').readlink()),'ppid':int(before[1]),
                    'uids':tuple(map(int,status['Uid'].split())),'gids':tuple(map(int,status['Gid'].split())),
                    'listenerAddresses':tuple(sorted(listeners))}
        after = (p/'stat').read_text().rpartition(')')[2].split()
        if before[19]!=after[19] or argv!=(p/'cmdline').read_bytes():raise ValueError('SOCKS identity changed')
        return qualify(observed)
    except (OSError, KeyError, IndexError) as failure:
        raise ValueError('current owned SOCKS unavailable') from failure


def require_owner():
    first = capture()
    if first != capture():raise ValueError('SOCKS owner unstable')
    return first
