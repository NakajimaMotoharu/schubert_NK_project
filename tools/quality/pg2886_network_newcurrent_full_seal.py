"""Whole currenta9/day15 post-Root pre-ownedstop seal. Never fabricate an admission preimage."""
import ast
import inspect
import json
import pg2704_operation_current_full_seal as prior
import pg2880_network_newday_rows as day
import pg2878_network_newcurrent_terminal as terminal
from pg2862_network_newcurrent_observer import SOURCE,BOM
from pg2814_network_newboot_readonly import BOOT,one
from pg1446_current_cold_stage import W

SLOT='pg2886-network-newcurrent-full-seal-v1'


def constant(raw,name,value):
    nodes=[n for n in ast.parse(raw).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id==name for t in n.targets)]
    if len(nodes)!=1:raise ValueError('one exact fullseal authority constant required '+name)
    node=nodes[0];return one(raw,ast.get_source_segment(raw,node),name+'='+repr(value))


def oracle(binding):
    raw=day.oracle_source().replace('def qualify(before,now,oracle,run,cutoff,upper):','def qualify_day(before,now,oracle,run,cutoff,upper):')
    raw+=r'''
def qualify(before,now,cutoff,done_end,upper):
 require(cutoff==CUT and instant(cutoff)<=instant(done_end)<=instant(upper))
 require(not any(row['business_date']=='2026-10-15'for row in before[BATCH]))
 expected=candidates(before,cutoff);inbox=classify_inbox(before,expected['inbox_scan_candidates'])
 return qualify_day(before,now,{'expected':expected,'expectedInbox':inbox},RUN,cutoff,upper)
'''
    import pg1766_next_day_independent_candidates as selectors
    selection='\n'.join(inspect.getsource(f)for f in [selectors.instant,selectors.older,selectors.candidates])
    raw+="\n_selection={'datetime':datetime,'UTC':datetime.timezone.utc};exec("+repr(selection)+",_selection)\ncandidates=_selection['candidates']\n"
    raw+='\n'+inspect.getsource(selectors.classify_inbox)
    raw+='\nUTC=datetime.timezone.utc\nRUN='+repr(binding['run'])+'\nCUT='+repr(binding['cutoff'])+'\n'
    from pyflakes.api import check
    if check(raw,'<whole before-based day15 fullseal oracle>'):raise ValueError('complete day15 independent oracle required')
    return raw


def payload(binding):
    actual=json.loads((W/'pg2876-network-admission-original-v2/manifest.safe.json').read_bytes())
    if actual.get('actualExit')!=0 or actual.get('productionSource')!=SOURCE:raise ValueError('actual immutable admission original required')
    before_hash=actual['guest']['privateBeforeSha256']
    raw=prior.payload(binding,BOM)
    for a,b in [(prior.SLOT,SLOT),(prior.SOURCE,SOURCE),('PG2654','PG2802'),('pg2654-manifest.sig','pg2802-manifest.sig'),
        ('b2d6f605-61cf-425f-8fbd-12d606f6ee66',BOOT),('b2d6f60561cf425f8fbd12d606f6ee66',BOOT.replace('-',''))]:raw=raw.replace(a,b)
    guard=terminal.payload(binding);marker="out=pathlib.Path('/var/lib/pgpt-s1-preservation/"+terminal.SLOT+"')"
    if guard.count(marker)!=1:raise ValueError('one genuine same-source terminal boundary required')
    raw=constant(raw,'GUARD',guard[:guard.index(marker)])
    raw=constant(raw,'ORACLE',oracle(binding))
    start=raw.index("before_raw=(BASE/'pg2684-operation-current-noargs-once-v2/before.private.json')")
    end=raw.index('\nOWNED={}',start)
    replacement="""before_raw=(BASE/'pg2872-network-newcurrent-noargs-once-v2/external-before.private.json').read_bytes()
require(hashlib.sha256(before_raw).hexdigest()==BEFORE_HASH)
captured=json.loads(before_raw);require(set(captured)=={'immutable','runtime','trees','observer'})
immutable=captured['immutable'];require(immutable['boot']==BOOT and immutable['source']=='04207efc3ad78bca75942153a90c70985064c988')
require(set(immutable['rows'])and len(immutable['rows'])==24)
before={'configuration':immutable['configuration'],'rows':immutable['rows'],'durable':immutable['durable']}
old['unitFilesActual']={name:value['metadata']+[value['sha256']]for name,value in immutable['unitFiles'].items()}
# Admission has no /run/systemd/system metadata snapshot. Do NOT invent one
# from after. Cold isolation admits the explicit empty no-override directory;
# signed Unit vectors/full32 effective declarations remain independently bound.
def isolation_runtime():
 root=pathlib.Path('/run/systemd/system');m=metadata(root)
 require(m[2:6]==[0,0,stat.S_IFDIR|0o755,2]and not os.listxattr(root)and not os.listdir(root))
 require(metadata(root)==m)
 return tree(root)
"""
    raw=raw[:start]+replacement+raw[end:]
    old=" runtime=tree(pathlib.Path('/run/systemd/system'));expected_runtime=before['oneTimeRuntime'];require(set(runtime)==set(expected_runtime))\n for path,v in runtime.items():require(v=={'metadata':expected_runtime[path]['metadata'],'sha256':expected_runtime[path]['sha256']})"
    raw=one(raw,old,' runtime=isolation_runtime()')
    raw='BEFORE_HASH='+repr(before_hash)+'\n'+raw
    from pyflakes.api import check
    if check(raw,'<whole actual a9 current day15 seal>'):raise ValueError('complete whole current seal namespace required')
    compile(raw,'<same current post-root pre-ownedstop full seal>','exec');return raw


def main():
    # Use the completed fullseal transport only; current terminal/rows/live are
    # the explicit prerequisites, never old current or another source successes.
    base=prior.previous.previous.prior.prior.previous.previous
    raw=inspect.getsource(base.main)
    for a,b in [('pg2021-fresh-resume-terminal-receipt-v1',terminal.SLOT),
        ('pg2023-fresh-resume-rows-oracle-v1','pg2880-network-newday-rows-v1'),
        ('pg2019-fresh-resume-live-binding-complete-v1','pg2874-network-newcurrent-live-binding-v1')]:raw=raw.replace(a,b)
    raw=raw.replace("payload(live['binding'])","payload({**live['binding'],'rootPid':live['rootPid']})")
    ns={**base.__dict__,'SOURCE':SOURCE,'SLOT':SLOT,'payload':payload}
    exec(compile(raw,'<whole current same-run seal dispatcher>','exec'),ns);return ns['main']()


if __name__=='__main__':raise SystemExit(main())
