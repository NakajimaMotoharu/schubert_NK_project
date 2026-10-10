"""SSC248 fixed pre-Ref Java11678/child11704 whole readonly qualification."""
import ast
import hashlib
import json
import re
from pg1050_cold_tree_preflight import payload as previous
from pg1041_cold_policy_diagnostic import W
from pg1051_cold_tree_preflight_v2 import dispatch

PARENT_ARGV='3ea4939c6ca3cfda762607633df876c68f6a6a66f21c1d40ba7c8d1b3a1c2ff4'
CHILD_ARGV='e80bc4b80bc445babd415b692ba52af71789bea599ae379587826905f29d1571'
ERROR='b41b40a23cce58f2be28bc8fcf88e2ac14d2b5f2ca882aeff88eb5f372f76447'


def once(text,old,new):
    if text.count(old)!=1:raise ValueError('fixed pre-Ref adaptation refused')
    return text.replace(old,new)


def payload():
    frozen=json.loads((W/'pg1075-cold-candidate-frozen-v2.safe.json').read_bytes())
    if frozen['actualExit']!=0 or frozen['operatorSource']!='9e9b91faefab576cbb1f1c574e22cd97f8214ebb':raise ValueError('fixed failed source required')
    root=W/'pg1074-cold-tools-v1'
    for name,digest in frozen['fileHashes'].items():
        if hashlib.sha256((root/name).read_bytes()).hexdigest()!=digest:raise ValueError('old failed payload changed')
    raw=previous()
    # Whole replacements are limited to fixed run/slot/actor literals. Source and
    # error hashes are explicit, not inferred from the future corrected payload.
    changes=[('PG1050-cold-tree-preflight-v1','PG1077-cold-candidate-tree-preflight-v1'),
             ('pg1037-cold-tools-v1','pg1074-cold-tools-v1'),('pg1037_cold_refs.py','pg1074_cold_refs.py'),
             ('pg1037-cold-prepared-v1','pg1074-cold-candidate-v1'),
             ('1373880','2433710'),('1373951','2433776'),
             ('fcb09442d0ad0bc9d0b71433c7a01f54b1c86941f3ab42e0c1cd6ba4f9f311c8',PARENT_ARGV),
             ('8067bb56195ab7f05b1427a9d5cf78f5d71e404000acc5f5f3391c5079e5a1d9',CHILD_ARGV),
             ('PG1037_REFS_UNKNOWN phase=BEFORE','PG1074_REFS_UNKNOWN phase=BYTE_AUTH'),
             ('ed0bd8d35e47d8e65cee98cc06f7eafccd8380ed9d715b5acb8cae9c253293f8',ERROR),
             ("env['PREPARED']=False","env['PREPARED']=True")]
    for old,new in changes:
        if old not in raw:raise ValueError('fixed old profile literal missing')
        raw=raw.replace(old,new)
    raw=re.sub(r'\b5463\b','11678',raw);raw=re.sub(r'\b5489\b','11704',raw)
    tree=ast.parse(raw)
    for node in tree.body:
        if isinstance(node,ast.Assign)and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
            if node.targets[0].id=='SOURCE_SHA':node.value=ast.Constant(hashlib.sha256((root/'pg1074_cold_refs.py').read_bytes()).hexdigest())
            elif node.targets[0].id=='PINS':node.value=ast.parse(repr(frozen['fileHashes']),mode='eval').body
    raw=ast.unparse(tree)+'\n'
    # Keep the frozen prepared namespace implementation, not pre-preparation layout.
    start=raw.index('def readonly_runtime_namespaces():');end=raw.index("env['runtime_namespaces'] = readonly_runtime_namespaces",start)
    raw=raw[:start]+raw[end+len("env['runtime_namespaces'] = readonly_runtime_namespaces\n"):]
    start=raw.index('    old_names = [');end=raw.index("    for name in env['old']['units']:",start)
    raw=raw[:start]+"    assert not [n for n in daemon.ListNames() if str(n).startswith(':') and int(daemon.GetConnectionUnixProcessID(n)) == 11704]\n"+raw[end:]
    raw=once(raw,"    before['childBusUniqueName'] = old_names[0]","    before['childNoBus'] = True")
    marker="    child = actor(11704, 2433776, '"+CHILD_ARGV+"', '/usr/bin/python3.14', set(), 11678)"
    raw=once(raw,marker,marker+"\n    assert set(child['fds']) == {'0', '1', '2'}\n    assert all(stat.S_ISFIFO(child['fds'][n]['metadata'][4]) for n in ('0', '1'))\n    assert stat.S_ISREG(child['fds']['2']['metadata'][4]) and child['fds']['2']['metadata'][6] == 75")
    raw=once(raw,"    phase = 'FIXED_TREE_AND_PEER'","    phase = 'FIXED_TREE_AND_PEER'\n    assert not os.path.lexists('/opt/schubert-nk/releases/0.1.0-PG1068') and not os.path.lexists('/var/lib/pgpt-s1-preservation/pg1068-manifest.sig')\n    assert {p.name for p in pathlib.Path('/var/lib/pgpt-s1-preservation/pg1074-cold-candidate-v1').iterdir()} == {'refs.private.log', 'tree-preflight-v1'}")
    marker="return {'tree': first, 'server': server, 'controls': control, 'snapshot': snapshot, 'heldWholeMetadata': safe(allheld)}"
    raw=once(raw,marker,"runtime=env['runtime_namespaces']();assert runtime==expected_runtime\n    "+marker[:-1]+", 'runtime':runtime}")
    marker="held = []\n"
    reference="prepared_raw=pathlib.Path('/var/lib/pgpt-s1-preservation/pg1062-cold-prepared-v1/after.private.json').read_bytes()\nassert hashlib.sha256(prepared_raw).hexdigest()=='412eb77968cd3f28d5bf2869df52b3625233809ba119b2b90cf9080e976516bf'\nexpected_runtime=json.loads(prepared_raw)['runtime']\n"
    raw=once(raw,'\n'+marker,'\n'+reference+marker)
    ast.parse(raw);return raw


if __name__=='__main__':dispatch('PG1077-cold-candidate-tree-preflight-v1','pg1077-cold-candidate-tree-preflight-v1',payload())
