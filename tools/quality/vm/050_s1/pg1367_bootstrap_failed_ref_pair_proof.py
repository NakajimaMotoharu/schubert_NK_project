"""Current failed1362 pair with one private helper Bus/ten Ref, no signal or setup."""
import pg1360_bootstrap_failed_pair_proof as previous
from pg1334_published_owned_stop_sources_v2 import SOURCE

def payload(seals):
    raw=previous.payload(seals).replace('Pg1356BootstrapExisting','Pg1362BootstrapExisting').replace('pg1356','pg1362')
    old="daemon=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus');require(not any(str(n).startswith(':')and int(daemon.GetConnectionUnixProcessID(n))in(pid,kid)for n in daemon.ListNames()))"
    if raw.count(old)!=1:raise ValueError('one actual child private Bus boundary required')
    raw=raw.replace(old,"daemon=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus');names=[str(n)for n in daemon.ListNames()if str(n).startswith(':')and int(daemon.GetConnectionUnixProcessID(n))==kid];require(len(names)==1 and not any(str(n).startswith(':')and int(daemon.GetConnectionUnixProcessID(n))==pid for n in daemon.ListNames()))")
    raw=raw.replace("'busNames0':True", "'bus':names,'tenRefsDeclaredBeforeFailure':True")
    raw=raw.replace('pg1360-bootstrap-failed-pair-v1','pg1367-bootstrap-failed-ref-pair-v1').replace('PG1360-bootstrap-failed-pair-v1','PG1367-bootstrap-failed-ref-pair-v1')
    compile(raw,'<actual failed current Ref pair>','exec');return raw

def source():
    return previous.source().replace('pg1360-bootstrap-failed-pair-v1','pg1367-bootstrap-failed-ref-pair-v1')

def main():
    env=dict(previous.previous.previous.prior.prior.previous.transport.__dict__,SOURCE=SOURCE,payload=payload)
    exec(compile(source(),'<current Ref pair proof transport>','exec'),env)
    return env['main']()

if __name__=='__main__':
    raise SystemExit(main())
