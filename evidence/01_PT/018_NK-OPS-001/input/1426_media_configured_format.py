"""Configured format-only correction; reuse successful unchanged PMD/CS, preserve original default failure."""
from pathlib import Path
import hashlib,json,shutil
import pg9666_pagination_static as c
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';TC=R.parent/'toolchain';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));old=B/'evidence/PG26974-media186-static-v1/manifest.json';raw=load(old);assert raw['actualExit']==0 and raw['stages']['format']['actualExit']==1 and raw['stages']['checkstyle']['actualExit']==0 and not raw['processingErrors'];assert all(sha(R/p)==h for p,h in raw['inputHashes'].items())
lineage=[];files=set()
for name in ['PG26810-web-auth-helper-current-static-v1','PG26872-snapshot-current-static-v1','PG26900-scenario-current-static-v1','PG26946-manifest-current-static-v1','PG26738-authorization-current-static-v1','PG26846-scenario-fatal-source-static-v1','PG26876-regenerator-fatal-source-static-v1','PG26928-media-fatal-source-static-v1','PG26974-media186-static-v1']:
 p=B/'evidence'/name/'manifest.json';m=load(p);cmd=m['stages']['format']['command'];paths=[Path(x) for x in cmd if x.endswith('.java')];assert paths
 for f in paths:
  rp=f.relative_to(R).as_posix();assert f.suffix=='.java' and not any(x in f.name for x in ['RootFailedStartRecoveryTest','RootFailedStartPairRecoveryTest','SnapshotKeyCloseWitness']);assert sha(f)==m['inputHashes'][rp];files.add(f)
 lineage.append(dict(manifest=ref(p),originalFormatExit=m['stages']['format']['actualExit'],sourcePaths=[str(f.relative_to(R)) for f in paths]))
O=B/'evidence/PG26978-media186-configured-static-v1';assert not O.exists();O.mkdir();c.SLOT=O
for label in ['pmd','checkstyle']:
 for suffix in ['-begin.safe.json','-process.safe.json','-exit.safe.json','.stdout','.stderr','.xml']:
  p=old.parent/(label+suffix)
  if p.exists():shutil.copyfile(p,O/p.name);assert sha(p)==sha(O/p.name)
cmd=[str(TC/'jdk-25.0.4/bin/java'),'-jar',str(TC/'google-java-format-1.36.1-all-deps.jar'),'--skip-reflowing-long-strings','--dry-run','--set-exit-if-changed',*[str(p) for p in sorted(files)]]
stage=c.step('format',cmd,R);assert stage['actualExit']==0 and not stage['timedOut'];assert all(sha(R/p)==h for p,h in raw['inputHashes'].items());stages=dict(raw['stages']);stages['format']=stage
v=dict(raw);v.update(actualExit=0,stages=stages,configuredFormat=True,configuredFlag='--skip-reflowing-long-strings',reusedUnchangedStages=['pmd','checkstyle'],reexecutedOnlyStage='configured-format',sourceLineage=lineage,configuredFormatSourceHashes={str(p.relative_to(R)):sha(p) for p in files},sourceOrExpectedChanged=False,originalDefaultFormatFailure=ref(old),originalBefore=ref(B/'evidence/PG26984-configured-formatter-before-v1/manifest.json'),productTestsExecuted=0,globalMavenFormatHoldStillTrue=True,toolSha256=sha(Path(__file__).resolve()));(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,configuredSources=len(files),lineageScopes=len(lineage),productTestsExecuted=0,rawPmd=len(v['rawFindings']),manifestSha256=sha(O/'manifest.json'))))
