"""S metadata only: reuse existing Jacoco analyzer; never run Product/tests/fixtures."""
import collections,hashlib,json,os,subprocess,sys,zipfile
from pathlib import Path
ROOT=Path.cwd()
BASE=ROOT/'documents/400_PGPT/470_PMO/500_SV計画整備_20261104'
SLOT=ROOT.parent/'pgpt-runs/PG379/pg18532-sv80-line-static-resume-v1'
PUBLIC=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18532-sv80-line-static-resume-v1'
PREFLIGHT=BASE/'575_静的line再開の未完限定入力.json'
SOURCE='6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
NORMAL_SHA='1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3'
TOOL=ROOT/'tools/quality/architecture/WholeSourceCoverageMeasureV1.java'
HELD_NAMES={'SnapshotKeyCloseWitness.java','pg9892_snapshot_key_close_witness.py','RootFailedStartRecoveryTest.java','RootFailedStartPairRecoveryTest.java'}
def sha(p):
 assert p.name not in HELD_NAMES
 return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,value):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
def main():
 mode=sys.argv[1];assert mode in ('preflight','run')
 if mode=='preflight':
  assert not PREFLIGHT.exists() and not SLOT.exists() and not PUBLIC.exists()
  oldPath=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG18530-sv80-missed-line-static-v1/manifest.json'
  assert sha(oldPath)=='e6c6db1a3f5b670fc037a689502b5b3d52268cea1340cc6c94e78745d65297e5'
  old=json.loads(oldPath.read_bytes());assert old['source']==SOURCE and old['actualExit']==1
  reuse=[r for r in old['results'] if r['terminal']['actualExit']==0];assert len(reuse)==10 and sum(len(r['sourceRows']) for r in reuse)==13
  skip={r['post'] for r in reuse};assert len(skip)==10
  normalPath=ROOT.parent/'pgpt-runs/PG379/pg14216-typed-marker-guard-six-compile-v1/manifest.safe.json'
  assert sha(normalPath)==NORMAL_SHA
  normal=json.loads(normalPath.read_bytes());assert normal['source']==SOURCE
  registry=json.loads((BASE/'503_Source証拠再利用判定.json').read_bytes())
  parts=[r for r in registry['rows'] if r['evidenceStatus']=='PARTIAL'];groups=collections.defaultdict(list)
  for r in parts:groups[r['qualifiedUnitProof']['post']].append(r)
  jobs=[]
  for name,rows in sorted(groups.items()):
   path=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'/name/'manifest.json'
   h=rows[0]['qualifiedUnitProof']['postSha256'];assert sha(path)==h
   if name in skip:continue
   post=json.loads(path.read_bytes());assert post['source']==SOURCE and post['actualExit']==0 and post['normalManifestSha256']==NORMAL_SHA
   paths={v for stage in post['stages'] for v in stage['command'] if isinstance(v,str) and v.startswith(str(ROOT.parent/'pgpt-runs/PG379')+'/') and v.endswith('/jacoco.exec')}
   assert len(paths)==1
   execPath=Path(next(iter(paths)));assert sha(execPath)==post['execSha256']
   md=set(post.get('metadataClasses') or []);exe=post['executable'];assert isinstance(exe,dict)
   physical={n for r in rows for n in r['qualifiedUnitProof']['physical']};assert physical<=set(exe)|md and not set(exe)&md
   for r in rows:
    outer=r['path'].split('/src/main/java/')[1][:-5];unit=post['fullSourceUnits'][outer]
    assert unit['totals']==r['counters'] and set(unit['physical'])==set(r['qualifiedUnitProof']['physical'])
    assert normal['begin']['inputHashes'][r['path']]==r['sha256']
   unexecuted={v.split('=',1)[1] for stage in post['stages'] for v in stage['command'] if isinstance(v,str) and v.startswith('--unexecuted=')}
   assert not unexecuted&md and unexecuted<=set(exe)
   jobs.append({'unexecuted':sorted(physical&unexecuted),'post':name,'postSha256':h,'execPath':str(execPath),'execSha256':post['execSha256'],'physical':sorted(physical),'metadata':sorted(physical&md),'rows':rows})
  assert len(jobs)==43 and sum(len(j['rows']) for j in jobs)==67
  jars={}
  for role,info in normal['jars'].items():assert sha(Path(info['path']))==info['sha256'];jars[role]=info
  home=ROOT.parent/'toolchain';jdk=home/'jdk-25.0.4'
  deps=[home/'m2/repository/org/jacoco/org.jacoco.core/0.8.15/org.jacoco.core-0.8.15.jar']+[home/('m2/repository/org/ow2/asm/'+n+'/9.10.1/'+n+'-9.10.1.jar') for n in ('asm','asm-tree','asm-commons')]
  value={'source':SOURCE,'scope':'STATIC_EXISTING_EXEC_ANALYZER_NOT_PRODUCT_EXECUTION','toolPath':str(TOOL),'toolSha256':sha(TOOL),'jdk':str(jdk),'javacSha256':sha(jdk/'bin/javac'),'javaSha256':sha(jdk/'bin/java'),'jdkReleaseSha256':sha(jdk/'release'),'dependencies':{str(p):sha(p) for p in deps},'normalManifestSha256':NORMAL_SHA,'jars':jars,'jobs':jobs,'reusedStaticSuccess':reuse,'originalFailureManifestSha256':sha(oldPath),'originalFailureManifest':str(oldPath),'newProductPT':0,'coverageAdded':0,'newAcceptance':0,'originalExecNotModified':True,'originalLogsRead':False,'heldPathsAccessed':False}
  write(PREFLIGHT,value)
  print(json.dumps({'actualExit':0,'phase':'PREFLIGHT','jobs':43,'newSources':67,'reuseSuccessPosts':10,'reuseSources':13,'sha256':sha(PREFLIGHT)}));return
 plan=json.loads(PREFLIGHT.read_bytes());assert plan['source']==SOURCE and sha(TOOL)==plan['toolSha256'];assert not SLOT.exists() and not PUBLIC.exists()
 for p,h in plan['dependencies'].items():assert sha(Path(p))==h
 for r in ('java','javac'):assert sha(Path(plan['jdk'])/'bin'/r)==plan[r+'Sha256']
 for info in plan['jars'].values():assert sha(Path(info['path']))==info['sha256']
 SLOT.mkdir();cp=':'.join(plan['dependencies']);classes=SLOT/'analyzer-classes';classes.mkdir()
 def invoke(command,directory):
  directory.mkdir(parents=True,exist_ok=False)
  start=__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()
  result=subprocess.run(command,cwd=ROOT,capture_output=True,timeout=60,check=False)
  for n,data in (('stdout',result.stdout),('stderr',result.stderr)):
   with (directory/(n+'.txt')).open('xb') as f:f.write(data);f.flush();os.fsync(f.fileno())
  assert len(result.stdout)<2_000_000 and len(result.stderr)<100_000
  item={'command':command,'actualExit':result.returncode,'startUTC':start,'endUTC':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),'stdoutSha256':sha(directory/'stdout.txt'),'stderrSha256':sha(directory/'stderr.txt'),'stdoutBytes':len(result.stdout),'stderrBytes':len(result.stderr)}
  write(directory/'terminal.json',item)
  return result,item
 compileCommand=[plan['jdk']+'/bin/javac','--release','25','-proc:none','-cp',cp,'-d',str(classes),str(TOOL)]
 compiled,compileMeta=invoke(compileCommand,SLOT/'compile')
 if compiled.returncode:write(PUBLIC/'manifest.json',{'actualExit':compiled.returncode,'phase':'TOOL_COMPILE_FAILED','source':SOURCE,'compile':compileMeta,'newProductPT':0});raise SystemExit(compiled.returncode)
 results=[]
 for ordinal,job in enumerate(plan['jobs'],1):
  assert sha(Path(job['execPath']))==job['execSha256']
  target=SLOT/('job-'+str(ordinal).zfill(2));target.mkdir();component=target/'component';component.mkdir()
  for r in job['rows']:
   role=r['module'].removeprefix('schubert-nk-')
   with zipfile.ZipFile(plan['jars'][role]['path']) as jar:
    for name in r['qualifiedUnitProof']['physical']:
     assert name.rsplit('/',1)[-1]+'.java' not in HELD_NAMES
     raw=jar.read(name+'.class');dest=component/(name+'.class');dest.parent.mkdir(parents=True,exist_ok=True)
     with dest.open('xb') as f:f.write(raw)
  names=[n for n in job['physical'] if n not in job['metadata'] and n not in job['unexecuted']]+['--unexecuted='+n for n in job['unexecuted']]+['--metadata='+n for n in job['metadata']]
  command=[plan['jdk']+'/bin/java','-cp',str(classes)+':'+cp,'WholeSourceCoverageMeasureV1',job['execPath'],str(component),*names]
  run,terminal=invoke(command,target/'analysis');sourceRows=[];rawLines=[];counterRows={}
  if run.returncode==0:
   for line in run.stdout.decode().splitlines():
    fields=line.split('\t')
    if fields[0]=='CLASS':counterRows[fields[1]]={v.split(':')[0]:{'missed':int(v.split(':')[1]),'covered':int(v.split(':')[2])} for v in fields[3:]}
    elif fields[0]=='MISSED_LINE':rawLines.append({'physical':fields[1],'sourceLine':int(fields[2]),'missedBranches':int(fields[3]),'coveredBranches':int(fields[4])})
   for r in job['rows']:
    physical=r['qualifiedUnitProof']['physical'];totals={k:{v:sum(counterRows[n][k][v] for n in physical if n in counterRows) for v in ('missed','covered')} for k in ('LINE','METHOD','CLASS','BRANCH')}
    assert totals==r['counters']
    sourceRows.append({'path':r['path'],'sha256':r['sha256'],'countersUnchanged':True,'lineAnchors':[x for x in rawLines if x['physical'] in physical]})
  results.append({'post':job['post'],'execSha256':job['execSha256'],'terminal':terminal,'sourceRows':sourceRows,'noProductClassLoaded':True,'oldExecUnchanged':sha(Path(job['execPath']))==job['execSha256']})
  write(target/'result.json',results[-1])
  print(json.dumps({'phase':'STATIC_ANALYSIS','completedPosts':ordinal,'of':43,'actualExit':run.returncode,'newProductPT':0}),flush=True)
  if run.returncode:break
 complete=len(results)==43 and all(r['terminal']['actualExit']==0 for r in results)
 manifest={'actualExit':0 if complete else 1,'source':SOURCE,'scope':'STATIC_REANALYSIS_EXISTING_HOST_EXEC_NOT_NEW_COVERAGE_OR_PT','preflightSha256':sha(PREFLIGHT),'toolSourceSha256':plan['toolSha256'],'compiledToolSha256':sha(classes/'WholeSourceCoverageMeasureV1.class'),'compile':compileMeta,'results':results,'reusedStaticSuccess':plan['reusedStaticSuccess'],'originalFailureManifestSha256':plan['originalFailureManifestSha256'],'complete':complete,'sourceRows':sum(len(r['sourceRows']) for r in results+plan['reusedStaticSuccess']),'lineAnchorRows':sum(len(s['lineAnchors']) for r in results+plan['reusedStaticSuccess'] for s in r['sourceRows']),'newProductExecutions':0,'currentNewPTPasses':0,'coverageAdded':0,'newAccepted':0,'formalUpdated':False,'oldSourcesNotTransferred':True,'oldPrivateLogsRead':False}
 write(PUBLIC/'manifest.json',manifest)
 print(json.dumps({'actualExit':manifest['actualExit'],'phase':'FINISHED','sha256':sha(PUBLIC/'manifest.json'),'sources':manifest['sourceRows'],'lineAnchors':manifest['lineAnchorRows'],'newProductPT':0}))
 raise SystemExit(manifest['actualExit'])
if __name__=='__main__':main()
