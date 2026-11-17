"""Previously unmeasured raw view of the original16 exec; no product/test definitions or execution."""
from pathlib import Path
import datetime,hashlib,json,subprocess,sys
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
postp=b/'evidence/PG29956-maintenance-records16-post-v2/manifest.json';post=ld(postp);pre=ld(r/post['preflight']['path']);prep=ld(r/pre['prepare']['path']);assert post['actualExit']==pre['actualExit']==prep['actualExit']==0 and post['tests']==16
assert sha(r/post['preflight']['path'])==post['preflight']['sha256'] and sha(r/pre['prepare']['path'])==pre['prepare']['sha256']
assert all(sha(r/n)==h for n,h in post['inputHashes'].items())
currentp=b/'evidence/PG37224-monitor-lock4-four-main-compile-v2/manifest.json';current=ld(currentp);assert current['actualExit']==0
lookup={n:(m,h) for m,rows in current['physicalClassHashes'].items() for n,h in rows.items()};names=sorted(prep['physicalClassHashes']);assert len(names)==6 and set(n[:-6] for n in names)==set(post['classIds'])
files=[]
for n,h in prep['physicalClassHashes'].items():
 m,now=lookup[n];assert h==now
 p=Path(current['cwd'])/('src/schubert-nk-'+m)/'target/classes'/n;assert sha(p)==h;files.append(p)
for name,h in post['dependencies'].items():assert sha(Path(name))==h
execp=postp.parent/'jacoco.exec';assert sha(execp)==post['files']['jacoco.exec']
info=postp.parent/'unit-execinfo.stdout';assert sha(info)==post['files']['unit-execinfo.stdout'] and info.read_text().count('Session "')==1
qualified=ld(b/'evidence/PG31432-generated-code-supplemental-tool-v1/compile.json');selftest=ld(b/'evidence/PG31434-generated-code-tool-selftest-v1/manifest.json');assert selftest['actualExit']==0 and selftest['toolTests']==12
for pin in qualified['dependencies']+[dict(path=str(r/qualified['source']['path']),sha256=qualified['source']['sha256'])]:assert sha(Path(pin['path']))==pin['sha256']
out=b/'evidence/PG37262-p00403-records16-unfiltered-reuse-v1';assert not out.exists();out.mkdir();tool=r.parent/'pgpt-runs/PG379/pg31432-generated-code-supplemental-tool-v1/toolclasses'
command=[str(r.parent/'toolchain/jdk-25.0.4/bin/java'),'-cp',':'.join([str(tool),*[x['path'] for x in qualified['dependencies']]]),'org.jacoco.core.internal.analysis.UnfilteredCodeMeasurement',str(execp),*map(str,files)]
start=datetime.datetime.now(datetime.timezone.utc).isoformat();run=subprocess.run(command,capture_output=True,timeout=120);(out/'measurement.stdout').write_bytes(run.stdout);(out/'measurement.stderr').write_bytes(run.stderr);assert run.returncode==0
classes={};methods=[]
for line in run.stdout.decode().splitlines():
 f=line.split('\t')
 if f[0]=='CLASS':
  assert len(f)==12;row=dict(name=f[1],id=f[2],dataPresent=f[3]=='true',probes=int(f[4]),access=int(f[5]),counters={});classes[f[1]]=row;offset=6
 else:
  assert f[0]=='METHOD' and len(f)==11;row=dict(className=f[1],name=f[2],descriptor=f[3],access=int(f[4]),counters={});methods.append(row);offset=5
 for item in f[offset:]:
  k,missed,covered=item.split(':');row['counters'][k]=dict(missed=int(missed),covered=int(covered))
assert set(classes)==set(post['classIds']) and all(row['id']==post['classIds'][n] for n,row in classes.items())
assert len(methods)==sum(post['actualJvmCodeMethodCounts'].values())==53
own={'dev/codex/schubert/nk/batch/file/MaintenanceRecords','dev/codex/schubert/nk/batch/repository/MaintenanceRetirement'}
totals={k:{role:sum(classes[n]['counters'][k][role] for n in own) for role in ['missed','covered']} for k in ['LINE','METHOD','CLASS','BRANCH','INSTRUCTION']}
missed=[m for m in methods if any(x['missed'] for x in m['counters'].values())]
assert sha(execp)==post['files']['jacoco.exec'] and all(sha(p)==prep['physicalClassHashes'][str(p.relative_to(Path(current['cwd'])/('src/schubert-nk-'+lookup[str(p).split('/target/classes/',1)[1]][0])/'target/classes'))] for p in files)
value=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),measurementStartUTC=start,sourceCore=current['sourceCore'],originalUnitSource=post['source'],originalRun=post['run'],originalTests=16,newProductTests=0,newMainDefinitions=0,originalPost=ref(postp),originalExec=ref(execp),originalPrepare=pre['prepare'],currentCompile=ref(currentp),inputHashes=post['inputHashes'],allSixClassHashesByteExact=prep['physicalClassHashes'],command=command,measurementExit=run.returncode,toolSource=qualified['source'],self12Replayed=False,standardCountersHistorical=post['completeSourceComponentCounters'],allPhysicalRetained=6,classes=classes,methods=methods,actualCodeMethods=53,missedCodeMethods=missed,ownedTwoProgramCounters=totals,ownedTwoAllCounters100=all(x['missed']==0 for x in totals.values()),manualExclusions=[],oldExecCombined=False,nativeQualificationTransferred=False,sameSourceWholeRunGateClaimed=False,newAcceptance=0,formalUpdated=False)
(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,oldTests16NotReplayed=True,methods53=True,ownedTwoRaw=totals,missedMethods=len(missed),newTests=0)))
