from pathlib import Path
import hashlib,json
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();p=B/'evidence/PG28152-backup-manifest16-pre-style-v1/manifest.json';m=ld(p);assert m['actualExit']==0 and m['preliminaryOnly'] and not m['fullQualityGateSatisfied'] and not m['rawFindings'] and not m['processingErrors'] and m['checkstyleFindings']==0 and len(m['inputHashes'])==10;seen=set()
for label,x in m['stages'].items():
 assert x['actualExit']==0 and not x['timedOut']
 for stream in ['stdout','stderr']:assert sha(p.parent/(label+'.'+stream))==x[stream+'Sha256']
 if label.startswith('format-'):
  path=str(Path(x['command'][-1]).relative_to(R));assert path in m['inputHashes'] and path not in seen;seen.add(path)
assert seen==set(m['inputHashes']) and len(m['stages'])==12
for path,h in m['inputHashes'].items():assert sha(R/path)==h
w=B/'evidence/PG28150-backup-manifest16-worker-fix-v1/manifest.json';fix=ld(w);assert fix['actualExit']==0 and len(fix['fixes'])==2 and fix['fixtureAndGoldenChanged']==False and all(x['inverseExactBeforeFormat'] and x['formatAllJavaTokensIdentical'] and x['formerAssertionsPreserved'] and sha(R/x['path'])==x['afterSha256'] for x in fix['fixes']);O=B/'evidence/PG28154-backup-manifest16-pre-style-admitted-v1';assert not O.exists();O.mkdir();m.update(originalPreStyle=dict(path=str(p.relative_to(R)),sha256=sha(p)),workerProof=dict(path=str(w.relative_to(R)),sha256=sha(w)),uniquePathCommands=10,productTestsReexecuted=0,verifierSha256=sha(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(dict(actualExit=0,uniquePathCommands=10,testsReexecuted=0))
