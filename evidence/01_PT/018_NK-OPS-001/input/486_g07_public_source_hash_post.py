"""Independent zero-candidate source-map boundary proof; no source byte I-O required."""
from pathlib import Path
from collections import Counter
import json,hashlib,re,datetime,copy
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';S=B/'evidence/PG23614-g07-public-source-hash-provenance-v1';O=B/'evidence/PG23616-g07-public-source-hash-independent-v1';load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');key=lambda v:tuple(v[n] for n in ['path','ruleId','startLine','endLine','inputSha256']);assert not O.exists();mp=S/'manifest.json';assert sha(mp)=='cf3759ab2107ddf199855c5f7fee27172be34f0824cabbd4cda9b6256e8bfe89';m=load(mp);cp=R/m['config']['path'];assert sha(cp)==m['config']['sha256'];cfg=load(cp);origin=R/cfg['originalMetadata']['path'];assert sha(origin)==cfg['originalMetadata']['sha256'];rows=load(origin);assert len(rows)==4493;original=Counter(map(key,rows));prior=[]
for ref in m['priorUpdateRefs']:
 p=R/ref['path'];assert sha(p)==ref['sha256'];prior+=load(p)
old=Counter(map(key,prior));assert len(prior)==190 and sum((original-old).values())==4303;expected=[];kept=[];typed=0
for path,pin in cfg['inputFiles'].items():
 assert re.fullmatch(r'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG[89][0-9]{3}-[A-Za-z0-9-]*host[A-Za-z0-9-]*/manifest\.json',path);p=R/path;assert sha(p)==pin;lines=p.read_text().splitlines(keepends=True);data=load(p);maps=[]
 for role in cfg['fieldRoles']:
  obj=data
  for n in role:obj=obj.get(n) if isinstance(obj,dict) else None
  if not isinstance(obj,dict):continue
  begin=0;end=len(lines)+1
  if len(role)==2:
   parents=[i for i,s in enumerate(lines,1) if s=='  "begin": {\n']
   if len(parents)!=1:continue
   begin=parents[0];end=next(i for i,s in enumerate(lines[begin:],begin+1) if s in ['  },\n','  }\n'])
  indent=' '*(2*len(role));starts=[i for i,s in enumerate(lines,1) if begin<i<end and s==indent+'"'+role[-1]+'": {\n']
  if len(starts)!=1:continue
  lo=starts[0];hi=next(i for i,s in enumerate(lines[lo:],lo+1) if s in [indent+'},\n',indent+'}\n']);maps.append((lo,hi,obj));typed+=1
 for f in [v for v in rows if v['path']==path and not old[key(v)]]:
  base={n:f[n] for n in ['path','ruleId','startLine','endLine','inputSha256']};assert f['inputSha256']==pin
  if f['ruleId']!='generic-api-key' or f['shape']!='ALL_HEX64' or f['startLine']!=f['endLine']:kept.append(dict(**base,status='UNKNOWN_UNSUPPORTED_RULE_SHAPE_OR_MULTILINE'));continue
  line=lines[f['startLine']-1];pair=re.fullmatch(r'\s+("(?:\\.|[^"\\])*"): "([a-f0-9]{64})",?\n?',line);selected=[v for v in maps if v[0]<f['startLine']<v[1]]
  assert pair is None or not selected,'unexpected eligible scalar needs a separately implemented source proof'
  kept.append(dict(**base,status='UNKNOWN_OUTSIDE_DECLARED_TYPED_SOURCE_HASH_MAP'))
assert typed==m['typedSourceHashMaps'];assert sha(S/'updates.json')==m['updatesSha256'] and sha(S/'retained.json')==m['retainedSha256'];assert load(S/'updates.json')==expected==[] and load(S/'retained.json')==kept;assert Counter(map(key,kept))==Counter(key(v) for v in rows if v['path'] in cfg['inputFiles'] and not old[key(v)]);assert len(kept)==m['candidateRows']==667;assert sha(R/m['tool']['path'])==m['tool']['sha256']
def contract(v):
 assert v['actualExit']==0 and v['newFalsePositives']==0 and v['remainingUnclassified']==4303 and v['actualSecretCount'] is None and v['binaryOrContainerLimited']==22 and v['sourceReadset']==[] and v['actualDistinctSourceFilesRead']==v['productTestsExecuted']==v['productClassesInitialized']==v['newCompilerExecutions']==v['actualBackendActions']==v['newAcceptance']==0 and all(v[n] is False for n in ['protectedOrDeniedSourceIo','originalProducerOrScannerExecuted','javaMainOrTestExecuted','privateRawOrRuntimeArchiveRead','oldOrCurrentRunQualified','wholeSourceIdentityQualified','wholeG07Accepted','whole451Accepted'])
contract(m);checks=0
for n,v in [('newFalsePositives',1),('actualSecretCount',0),('sourceReadset',['forbidden']),('actualDistinctSourceFilesRead',1),('protectedOrDeniedSourceIo',True),('javaMainOrTestExecuted',True),('oldOrCurrentRunQualified',True),('wholeG07Accepted',True),('whole451Accepted',True)]:
 bad=copy.deepcopy(m);bad[n]=v
 try:contract(bad)
 except AssertionError:checks+=1
 else:raise AssertionError('false source-map credit')
O.mkdir();out=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),producerManifest=dict(path=str(mp.relative_to(R)),sha256=sha(mp)),inputFiles=cfg['inputFiles'],candidateRows=667,typedSourceHashMaps=typed,newFalsePositives=0,remainingUnclassified=4303,actualSecretCount=None,binaryOrContainerLimited=22,retainedStatusCounts=dict(Counter(v['status'] for v in kept)),sourceFilesRead=0,productTestsExecuted=0,productClassesInitialized=0,newCompilerExecutions=0,actualBackendActions=0,metadataNegativeChecks=checks,oldOrCurrentRunQualified=False,wholeSourceIdentityQualified=False,wholeG07Accepted=False,whole451Accepted=False,newAcceptance=0,formalUpdated=False,effortRate=None,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))));write(O/'manifest.json',out);print(json.dumps(dict(actualExit=0,newFalsePositives=0,remaining=4303,metadataNegativeChecks=checks,manifestSha256=sha(O/'manifest.json'))))
