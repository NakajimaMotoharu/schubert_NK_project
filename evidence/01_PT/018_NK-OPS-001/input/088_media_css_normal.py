"""New-only normal Main/POM resource build; test names excluded before content acquisition."""
from pathlib import Path
import json,hashlib,subprocess,tarfile,io,sys,zipfile,datetime
import pg9666_pagination_static as capture
R=Path.cwd();W=R.parent/'pgpt-runs/PG379';SLOT=W/'pg20704-media-css-six-main-resource-compile-v1';oldPath=W/'pg20586-question-menu-six-main-resource-compile-v1/manifest.safe.json';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();write=lambda p,d:Path(p).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');source=sys.argv[1];assert len(source)==40 and subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()==source;assert not SLOT.exists();old=json.loads(oldPath.read_text());assert sha(oldPath)=='fc1d464e00926ca61857fd64949737259f3c184279b2f136613989ea8844c6fc' and old['actualExit']==0
names=sorted(old['begin']['inputHashes']);assert len(names)==1035 and all(((n.startswith('src/') and ('/src/main/' in n or n.endswith('pom.xml'))) or n in {'pom.xml','program/characterization/pom.xml'}) and '/src/test/' not in n and '..' not in Path(n).parts and not any(s in n for s in ['RootFailedStartRecoveryTest','RootFailedStartPairRecoveryTest','SnapshotKeyCloseWitness','pg9892_snapshot_key_close_witness']) for n in names)
currentNames=subprocess.check_output(['git','ls-tree','-r','--name-only',source],text=True).splitlines();eligible=sorted(n for n in currentNames if (n.startswith('src/') and ('/src/main/' in n or n.endswith('pom.xml'))) or n in {'pom.xml','program/characterization/pom.xml'});assert names==eligible
SLOT.mkdir();snapshot=SLOT/'snapshot';snapshot.mkdir();archive=subprocess.check_output(['git','archive',source,'--',*names]);archiveHash=hashlib.sha256(archive).hexdigest()
with tarfile.open(fileobj=io.BytesIO(archive),mode='r:') as tar:
 for member in tar.getmembers():assert not member.name.startswith('/') and '..' not in Path(member.name).parts and (member.isfile() or member.isdir()) and not member.issym() and not member.islnk()
 tar.extractall(snapshot,filter='data')
inputs={n:sha(snapshot/n) for n in names};assert all(inputs[n]==sha(R/n) for n in names)
changed=[n for n in names if inputs[n]!=old['begin']['inputHashes'][n]];assert changed==['src/schubert-nk-web/src/main/resources/static/css/schubert.css']
command=old['begin']['command'];assert '-Dmaven.test.skip=true' in command and command[-1]=='package' and sha(command[0])==old['begin']['mavenSha256'];begin=dict(source=source,archiveSha256=archiveHash,inputHashes=inputs,command=command,mavenSha256=sha(command[0]),testsExcludedBeforeContentRead=True,testStatus='NOT_RUN_COMPILE_ONLY_NOT_PASS',noRootInvocation=True,actualBackendActions=0,changes=changed,producerPath=str(Path(__file__).resolve().relative_to(R)),producerSha256=sha(__file__),startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat());write(SLOT/'begin.safe.json',begin);capture.SLOT=SLOT;terminal=capture.step('compile',command,snapshot,timeout=180)
result=dict(actualExit=terminal['actualExit'],source=source,begin=begin,terminal=terminal,testsExecuted=False,testStatus='NOT_RUN_COMPILE_ONLY_NOT_PASS',whole451Accepted=False,formalUpdated=False,jars={},sourceInputsUnchanged=all(sha(R/n)==h for n,h in inputs.items()),nullAwayConfiguration=dict(pomBytesUnchanged=True,reference=old['nullAwayConfiguration']))
if terminal['actualExit']==0:
 oldClasses={};newClasses={}
 for module in old['jars']:
  jar=snapshot/f'src/schubert-nk-{module}/target/schubert-nk-{module}-0.1.0-SNAPSHOT.jar';assert jar.is_file();result['jars'][module]=dict(path=str(jar),sha256=sha(jar))
  for current,dest in [(Path(old['jars'][module]['path']),oldClasses),(jar,newClasses)]:
   with zipfile.ZipFile(current) as z:
    for n in z.namelist():
     if n.endswith('.class'):dest[module+':'+n]=hashlib.sha256(z.read(n)).hexdigest()
 assert set(oldClasses)==set(newClasses) and len(oldClasses)==1844
 drift=[n for n in oldClasses if oldClasses[n]!=newClasses[n]];assert drift==[]
 result['classIdentity']=dict(referenceSource=old['source'],referenceNormalManifestSha256=sha(oldPath),physicalClasses=1844,codeOrDebugDifferences=0,allJavaMainSourceBytesUnchanged=True,allPomBytesUnchanged=True,notRuntimeOrWholeReleaseQualification=True)
 result['normalPhysicalClassHashes']=newClasses
write(SLOT/'manifest.safe.json',result);assert result['sourceInputsUnchanged'];print(json.dumps(dict(actualExit=result['actualExit'],testsExecuted=False,classes=1844 if result['jars'] else None,manifestSha256=sha(SLOT/'manifest.safe.json'))));sys.exit(terminal['actualExit'])
