"""New-only stopped PG932 placement, authenticated PG935 baseline, current remains e016.
No startup/retirement/publication/migration authority is added by this tool.
"""
import ast,subprocess,sys
from pathlib import Path
from pg863_stage_candidate_v6 import source as previous
R=Path(__file__).resolve().parent
TREE_PROJECTION='''
def retained_trees(record):
 trees={}
 for field in ('originals','backup','credentials','startup','oldProofs','native'):
  entries=record[field]
  assert type(entries)is dict and entries
  for name,row in entries.items():
   path=pathlib.Path(name)
   assert path.is_absolute()and str(path)==name and type(row)is dict
   assert set(row)=={'metadata','sha256'}and type(row['metadata'])is list and len(row['metadata'])==9
   roots=[p for p in (path,*path.parents)if str(p)in entries]
   root=str(roots[-1]);target=trees.setdefault(root,{})
   if name in target:assert target[name]==row
   target[name]=row
 return trees
baseline['trees']=retained_trees(baseline)
assert baseline['source']=='e01612fcd7f2752df5ae0836b78538fd5e87f120'
assert baseline['manifestSha256']=='20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe'
'''
def source():
    raw=previous().replace('PG863','PG936').replace('pg863','pg936')
    raw=raw.replace('PG862','NEXT_PG932').replace('pg862','NEXT_pg932').replace('PG832','PG862').replace('pg832','pg862').replace('NEXT_PG932','PG932').replace('NEXT_pg932','pg932')
    changes=(("SOURCE = 'e01612fcd7f2752df5ae0836b78538fd5e87f120'","SOURCE = '40ef6e894573d2ffab1d1732124960f9c98d5f97'"),('20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe','b75e8bd539edf40d1324896a16e51842d00a3983ba1eae661c86ab68d4692524'),('8bcb3453c182be8f0719818899ec3bd7e86070f7b02086015ecc33c27e10b977','20b99d2f913228f5a23c3ec62cf4ced9e6bc49554cd205f6e5546ad278c468fe'),('pg861-runtime841-retired-post-v1','pg935-current-preflight-v1'),('4bd686da5660104c6dc6975baa468fd80a015e5ecfcc3896fc26b4f9e2147579','4aa97f5a256d8d74283f83310b6c8e042dc0f8ca0bcd957bc68abed2fce257cb'),('==564','==584'),('== 564','== 584'))
    for old,new in changes:assert old in raw,old;raw=raw.replace(old,new)
    tree=ast.parse(raw);node=next(n for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='PAYLOAD'for t in n.targets));body=node.value.value
    marker=' baseline=json.loads(baseline_raw)';assert body.count(marker)==1
    body=body.replace(marker,marker+'\n'+''.join(' '+l+'\n'for l in TREE_PROJECTION.splitlines()))
    ast.parse(body);lines=raw.splitlines(keepends=True);raw=''.join(lines[:node.lineno-1])+'PAYLOAD='+repr(body)+'\n'+''.join(lines[node.end_lineno:]);ast.parse(raw);return raw
def payload():
    return next(n.value.value for n in ast.parse(source()).body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='PAYLOAD'for t in n.targets))
if __name__=='__main__':
    if sys.argv[1:]==['preflight']:
        body=payload();body=body[:body.index(" root=pathlib.Path('/opt/schubert-nk/releases/0.1.0-PG932')")]
        body+=' assert not os.path.lexists("/opt/schubert-nk/releases/0.1.0-PG932") and not os.path.lexists("/var/lib/pgpt-s1-preservation/pg932-manifest.sig")\nprint("PG936_PREFLIGHT current187/all24-584/full32/allretainedtrees/native/tenRefsClosed PASS mutation0")\n'
        p=Path('/home/mini/codex/project1/work/pgpt-vm/private');cmd=['ssh','-i',str(p/'vm-access'),'-oBatchMode=yes','-oIdentitiesOnly=yes','-oStrictHostKeyChecking=yes','-oUserKnownHostsFile='+str(p/'known_hosts'),'-p','22222','ubuntu@127.0.0.1','sudo -n python3 -B -']
        raise SystemExit(subprocess.run(cmd,input=body.encode()).returncode)
    assert not sys.argv[1:]
    exec(compile(source(),'<936 stopped same-source candidate placement>','exec'),{'__file__':str(R/'pg936_stage_candidate.py'),'__name__':'__main__'})
