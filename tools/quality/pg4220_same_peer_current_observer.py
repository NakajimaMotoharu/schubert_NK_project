"""SSC290 new immutable observer; identical actor/HTTP/TLS oracle, lower-fork manager transport."""
import ast
from pathlib import Path
import pg4012_literal_invariant_current_observer as previous
import pg4216_same_peer_observer_manager as transport
from pg1674_critical_management_gate import management_gate
from pg1446_current_cold_stage import P

PREFIX='pg4220'
SOURCE,BOM=previous.SOURCE,previous.BOM


def watch():
    raw=previous.namespace()['files']()['pg4012_watch_parent.py']
    node=next(n for n in ast.parse(raw).body if isinstance(n,ast.FunctionDef)and n.name=='manager')
    old=ast.get_source_segment(raw,node)
    raw=raw.replace(old,"def manager(role):\n    return reader.read(UNITS[role])",1)
    marker='seen=False;roots={};ready=set();proxy=False;prior=None;deadline=time.monotonic()+1900;morning=None\n'
    if raw.count(marker)!=1:raise ValueError('same finite watch clock boundary required')
    head,body=raw.split(marker)
    head='import pg4216_same_peer_observer_manager as observer_transport\n'+head
    setup="reader=observer_transport.NativeReader();held=[]\ntry:\n    for unit in sorted(observer_transport.NAMES):\n        reader.LoadUnit(unit);reader.RefUnit(unit);held.append(unit)\n"
    tail="finally:\n    try:\n        for unit in reversed(held):reader.UnrefUnit(unit)\n    finally:reader.close()\nprint(json.dumps({'observerTenMetadataRefsNormalClose':True,'automaticStartStop':False,'wholeMorningAccepted':False}),flush=True)\n"
    return head+setup+''.join('    '+line+'\n'for line in(marker+body).splitlines())+tail


def source():
    raw=previous.source().replace('pg4012',PREFIX).replace('PG4012','PG4220')
    marker="def files():return {'pg4220_watch_parent.py':watch(),**{n:(R/n).read_text()for n in('pg457_stable_actor.py','pg462_observer_identity.py')}}"
    if raw.count(marker)!=1:raise ValueError('one existing closed observer bundle required')
    raw=raw.replace(marker,"def files():return OBSERVER_FILES\n",1)
    return raw


def namespace():
    old=previous.namespace()['files']()
    files={'pg4220_watch_parent.py':watch(),**{k:v for k,v in old.items()if k!='pg4012_watch_parent.py'},
           'pg4216_same_peer_observer_manager.py':Path(transport.__file__).read_text()}
    ns={'__file__':str(Path(previous.__file__).parent/'vm/050_s1/pg4220_same_peer_current_observer.py'),'__name__':'same_peer_current_observer','OBSERVER_FILES':files}
    exec(compile(source(),'<new immutable same-peer observer>','exec'),ns);return ns


def main():
    import sys
    if sys.argv[1:]==['stage']:
        with management_gate(P/'current-management-critical.lock'):return namespace()['main']()
    return namespace()['main']()


if __name__=='__main__':raise SystemExit(main())
