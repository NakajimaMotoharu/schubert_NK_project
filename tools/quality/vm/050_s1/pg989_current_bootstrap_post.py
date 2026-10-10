"""Actual captured normal exit20 first, then current full32 under tenRefs; read-only."""
import ast,json
from pathlib import Path
R=Path(__file__).resolve().parent;W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
def base_source():
    raw=(R/'pg901_bootstrap_post.py').read_text()
    for a,b in (('from pg895_bootstrap_before import payload as previous,W,P','from pg981_current_bootstrap_before_v2 import payload as previous,W,P'),('from pg894_sources_v3 import files','from pg983_current_bootstrap_sources import files'),('pg894','pg983'),('pg895-bootstrap-before-v1','pg978-bootstrap-before-v2'),('pg885','pg960'),('pg890','pg968'),('pg887','pg963'),('pg901-bootstrap-post-v1','pg989-bootstrap-post-v3'),('PG901-bootstrap-post-v1','PG989-bootstrap-post-v3'),('2a4f222e0d9759ac7c764f3e3c581a9774ad74de01971f15bf28e759dbc04e6e','be3ea723300b870ed2dce9477a5666bd9b59d7cc5fe7fc682e1cbbd26afec0cd')):
        assert a in raw,a;raw=raw.replace(a,b)
    assert raw.count('PG895-bootstrap-before-v1')==1
    raw=raw.replace('PG895-bootstrap-before-v1','PG978-bootstrap-before-v2')
    ast.parse(raw);return raw
def base_namespace():
    env={'__file__':str(R/'pg989_current_bootstrap_post.py'),'__name__':'current_bootstrap_post_definitions'}
    exec(compile(base_source(),'<989 actual current source base post>','exec'),env);return env
def payload(proof,seals):
    raw=base_namespace()['payload'](proof,seals)
    assert "'run':'PG989-bootstrap-post-v3'" in raw
    hashes=json.loads((W/'pg983-frozen-v3.safe.json').read_bytes())['fileHashes']
    authenticate='''
tools=base/'pg983-bootstrap-tools-v3'
require({p.name for p in tools.iterdir()}==set(BOOT_HASHES)|{'payload-sha256.json'})
for name,digest in BOOT_HASHES.items():
 p=tools/name;s=p.lstat();require(stat.S_ISREG(s.st_mode)and(s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode),s.st_nlink)==(0,0,0o400,1)and hashlib.sha256(p.read_bytes()).hexdigest()==digest)
require(json.loads((tools/'payload-sha256.json').read_bytes())==BOOT_HASHES)
current_bootstrap=show(bootstrap,STATE_FIELDS)
require(current_normal_or_gc(terminal,current_bootstrap))
current_configuration=complete_configuration(command(['systemctl','show',bootstrap,'--property='+','.join(sorted(FIELDS))]).decode(),bootstrap)
require(CONFIG['same'](boot_after['configuration'][bootstrap],current_configuration,exec_record))
after={**after,'units':{**after['units'],bootstrap:current_bootstrap},'configuration':{**after['configuration'],bootstrap:current_configuration}}
'''
    marker='bus=dbus.SystemBus(private=True);';assert raw.count(marker)==1
    raw=raw.replace(marker,(R/'pg902_terminal_current.py').read_text()+'\n'+authenticate+'\n'+marker)
    start=raw.index('current_bootstrap=show(bootstrap,STATE_FIELDS)');end=raw.index('\n\nbus=dbus.SystemBus',start)
    block=raw[start:end];raw=raw[:start]+raw[end:]
    marker=' for u in UNITS:manager.LoadUnit(u);manager.RefUnit(u);refs.append(u)';assert raw.count(marker)==1
    raw=raw.replace(marker,marker+'\n'+''.join(' '+line+'\n'for line in block.splitlines()))
    marker="result['currentCredentialsRetired']=True";assert raw.count(marker)==1
    raw=raw.replace(marker,marker+"\nresult['capturedNormal20VerifiedBeforeCurrent']=True\nresult['currentGcHistoryEmpty']=current_bootstrap!=terminal\nresult['gcDoesNotInferPastSuccess']=True")
    assert raw.index('manager.LoadUnit(u)')<raw.index('current_bootstrap=show')<raw.index(' def snapshot():')
    ast.parse(raw);return 'BOOT_HASHES='+repr(hashes)+'\n'+raw
if __name__=='__main__':
    env=base_namespace();env['payload']=payload;env['main']()
