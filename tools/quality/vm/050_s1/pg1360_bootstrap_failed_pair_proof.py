"""Current failed Java/helper pair, DB already gone, no old normal-close inference."""
import pg1352_bootstrap_expired_peer_proof as previous
from pg1334_published_owned_stop_sources_v2 import SOURCE

def payload(seals):
    raw = previous.payload(seals).replace('Pg1348BootstrapExisting', 'Pg1356BootstrapExisting').replace('pg1348', 'pg1356')
    raw = raw.replace('locks[name]=metadata9(st)', 'locks[name]=list(metadata9(st))')
    old = "kids={x for t in(p/'task').iterdir()for x in(t/'children').read_text().split()};require(not kids)"
    if raw.count(old) != 1:
        raise ValueError('one exact current child boundary required')
    raw = raw.replace(old, '''kids={x for t in(p/'task').iterdir()for x in(t/'children').read_text().split()};require(len(kids)==1);kid=int(next(iter(kids)));c=pathlib.Path('/proc')/str(kid)
 child_status=dict(x.split(':',1)for x in(c/'status').read_text().splitlines()if ':'in x);child_argv=(c/'cmdline').read_bytes();args=child_argv.split(b'\\0')
 require(str((c/'exe').readlink())=='/usr/bin/python3.14'and args[:4]==[b'/usr/bin/python3',b'-B',b'/var/lib/pgpt-s1-preservation/pg1356-bootstrap-tools-v3/pg1356_bootstrap_existing.py',b'verify']and len(args)==6 and args[4].isdigit()and args[5]==b'')
 require(int(child_status['PPid'])==pid and child_status['Uid'].split()==child_status['Gid'].split()==['0']*4 and child_status['Groups'].split()==['0']and all(not(t/'children').read_text().strip()for t in(c/'task').iterdir()))
 daemon=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus');require(not any(str(n).startswith(':')and int(daemon.GetConnectionUnixProcessID(n))in(pid,kid)for n in daemon.ListNames()))
 child={'pid':kid,'ticks':int((c/'stat').read_text().rpartition(')')[2].split()[19]),'argvSha256':hashlib.sha256(child_argv).hexdigest(),'exe':'/usr/bin/python3.14','busNames0':True}
''')
    raw = raw.replace("require({x.name for x in root.iterdir()}==set())", "require({x.name for x in root.iterdir()}=={'refs-prepare.private.log'})")
    raw = raw.replace("'expiredDbPeerGone':True", "'expiredDbPeerGone':True,'child':child")
    raw = raw.replace('pg1352-bootstrap-expired-peer-v1', 'pg1360-bootstrap-failed-pair-v1').replace('PG1352-bootstrap-expired-peer-v1', 'PG1360-bootstrap-failed-pair-v1')
    compile(raw, '<actual failed current Java/helper pair>', 'exec')
    return raw

def source():
    return previous.source().replace('pg1352-bootstrap-expired-peer-v1', 'pg1360-bootstrap-failed-pair-v1')

def main():
    env = dict(previous.previous.prior.prior.previous.transport.__dict__, SOURCE=SOURCE, payload=payload)
    exec(compile(source(), '<actual fixed failed pair proof>', 'exec'), env)
    return env['main']()

if __name__ == '__main__':
    raise SystemExit(main())
