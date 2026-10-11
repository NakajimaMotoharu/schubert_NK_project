"""One exact retained Ref helper then Java TERM; independent Ref holds all post checks."""
import ast
import pg1361_bootstrap_fixed_pair_handoff as original
import pg1367_bootstrap_failed_ref_pair_proof as proof
from pg1334_published_owned_stop_sources_v2 import SOURCE

PROOF='114a8dcdc6871a18354b2182e7ba32b36670cca4206206eb6d6722698922eb2f'

def payload(seals):
    raw=original.payload(seals)
    for old,new in (
        (original.PROOF,PROOF),('pg1360-bootstrap-failed-pair-v1','pg1367-bootstrap-failed-ref-pair-v1'),
        ('pg1361-bootstrap-fixed-pair-handoff-v1','pg1368-bootstrap-fixed-ref-handoff-v1'),
        ('PG1361-bootstrap-fixed-pair-handoff-v1','PG1368-bootstrap-fixed-ref-handoff-v1'),
        ('PG1361_RECOVERY','PG1368_RECOVERY'),
        ('839626','840449'),('7753101','7784890'),('839655','840478'),('7753240','7785030'),
        ('4d34aeae7feb470287f972b652f1603ceecaf75cd91686eea9c17019f449f0cf','68233c1d4b72c68a283ab97cba70016fd72d3d4398cc163e117abba34e2a4a82'),
        ('8805b2a9cc0ffda56de123acc4deb05a74a80859e8dc7c15788f5e06aeb68efd','501bccd8021ac84dc362ba34d63434491e200ff6d1ce184ccd49fa75dd49cb79')):
        if old not in raw:raise ValueError('complete actual Ref handoff binding required')
        raw=raw.replace(old,new)
    actual=proof.payload(seals);tree=ast.parse(actual)
    replacement={n.name:ast.get_source_segment(actual,n)for n in tree.body if isinstance(n,ast.FunctionDef)and n.name in{'candidate','fixed_owner'}}
    parent=replacement['fixed_owner'].replace('def fixed_owner():','def parent_only():')
    start=parent.index(' kids=');end=parent.index(' q=',start)
    parent=parent[:start]+" require(not pathlib.Path('/proc/840478').exists()and all(not(t/'children').read_text().strip()for t in(p/'task').iterdir()))\n"+parent[end:]
    replacement['parent_only']=parent.replace("'child':child","'child':None")
    for n in reversed(ast.parse(raw).body):
        if isinstance(n,ast.FunctionDef)and n.name in replacement:
            lines=raw.splitlines(keepends=True);raw=''.join(lines[:n.lineno-1])+replacement[n.name]+'\n'+''.join(lines[n.end_lineno:])
    marker=' terminate_once(840478,7785030,verify,reserve,os.pidfd_open,send,wait,os.close)'
    if raw.count(marker)!=1:raise ValueError('one actual child TERM required')
    raw=raw.replace(marker,marker+"\n daemon=dbus.Interface(bus.get_object('org.freedesktop.DBus','/org/freedesktop/DBus'),'org.freedesktop.DBus');require(not daemon.NameHasOwner(':1.616878'))")
    compile(raw,'<actual Ref then Java owned handoff>','exec');return raw

def source():
    return proof.source().replace('pg1367-bootstrap-failed-ref-pair-v1','pg1368-bootstrap-fixed-ref-handoff-v1')

def main():
    env=dict(proof.previous.previous.previous.prior.prior.previous.transport.__dict__,SOURCE=SOURCE,payload=payload)
    exec(compile(source(),'<actual Ref handoff transport>','exec'),env)
    return env['main']()

if __name__=='__main__':
    raise SystemExit(main())
