"""Passive inspection of exact 27 helper outputs in one saved host compiler snapshot, no compile/runtime."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess
R=Path(__file__).resolve().parents[4];B=R/'evidence/01_PT/018_NK-OPS-001';O=B/'evidence/PG23208-legacy-helper-output-binding-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_text())
blocked=('RootFailedStartRecoveryTest','RootFailedStartPairRecoveryTest','SnapshotKeyCloseWitness','pg9892_snapshot_key_close_witness','FingerprintKeyRing','ResponseSnapshotCodec','TemporaryInfrastructureException','WebStartupException')
def permitted(p):
 assert not any(s in str(p) for s in blocked)
 assert not any(s in p.parts for s in ('private','guest','raw'))
 return p
ip=B/'evidence/PG23202-thirty-helper-nested-hash-schema-v1/manifest.json';idx=load(ip);hs=[v for v in idx['helperRows'] if not v['receiptCount']];assert len(hs)==27
cp=B/'evidence/provisional/PG10024-test-hygiene-six-compile-v1/manifest.json';c=load(cp);cmd=c['begin']['command'];assert c['actualExit']==c['terminal']['actualExit']==0 and c['testsExecuted']==0 and c['testStatus']=='UNRUN_NOT_PASS_COMPILE_ONLY';assert isinstance(cmd,list) and 'package' in cmd and '-DskipTests=true' in cmd
snapshot=R.parent/'pgpt-runs/PG379/pg10024-test-hygiene-six-compile-v1/snapshot'
rows=[]
for v in hs:
 n=v['helper'];p=permitted(R/n);assert n.startswith('src/') and '/src/test/java/' in n and p.suffix=='.java';assert not p.is_symlink();current=sha(p);assert current==v['currentSourceSha256'];module=n.split('/')[1];fqn=v['declaredFqnFromSource'];assert re.fullmatch(r'dev\.codex\.schubert\.nk(?:\.[A-Za-z_$][\w$]*)+',fqn)
 key=module.removeprefix('schubert-nk-');jar=Path(c['jars'][key]['path']);expected=snapshot/'src'/module/'target';assert jar.parent==expected and jar.suffix=='.jar';d=permitted(expected/'test-classes');relative=fqn.replace('.','/')+'.class';cl=permitted(d/relative)
 assert cl.is_relative_to(snapshot) and not any(x.is_symlink() for x in [snapshot,snapshot/'src',snapshot/'src'/module,expected,d])
 pinned=c['begin']['inputHashes'].get(n)==current
 row=dict(helper=n,currentSourceSha256=current,compilerInputSourceHash=c['begin']['inputHashes'].get(n),sourcePinCurrent=pinned,declaredFqn=fqn,candidateOutput=str(cl),candidateBasis='MAVEN_CONVENTION_DERIVED_FROM_RECORDED_JAR_PATH_NOT_RECORDED_TEST_OUTPUT_DIGEST',originalClassDigestAvailable=False,originalCompileTimeBinaryIdentityProven=False)
 if pinned:
  assert not cl.is_symlink()
  if cl.is_file():
   data=cl.read_bytes();assert data[:4]==bytes.fromhex('cafebabe');major=int.from_bytes(data[6:8],'big');assert major==69
   nested=[]
   for np in sorted(cl.parent.glob(cl.stem+'$*.class')):
    permitted(np);assert np.is_file() and not np.is_symlink();nd=np.read_bytes();assert nd[:4]==bytes.fromhex('cafebabe') and int.from_bytes(nd[6:8],'big')==69;nested.append(dict(name=np.name,sha256=hashlib.sha256(nd).hexdigest()))
   row.update(status='CURRENT_SOURCE_PIN_SAVED_OUTPUT_PRESENT_ORIGINAL_BINARY_IDENTITY_UNPROVEN',observedOuterSha256=hashlib.sha256(data).hexdigest(),classMajor=major,nestedObservedFiles=nested)
  else: row.update(status='CURRENT_SOURCE_PIN_SAVED_OUTPUT_NOT_FOUND_NOT_TEST_FAILURE',nestedObservedFiles=[])
 else:row.update(status='SOURCE_PIN_NOT_CURRENT_OUTPUT_NOT_READ',nestedObservedFiles=[])
 rows.append(row)
assert not O.exists();O.mkdir()
v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),compilerManifest=dict(path=str(cp.relative_to(R)),sha256=sha(cp),source=c['source'],actualExit=c['actualExit'],testsExecuted=0,testStatus=c['testStatus'],goal='package',skipTests=True,pomPreflightPluginDeclarations=len(c['begin']['pomPreflight'])),helperIndex=dict(path=str(ip.relative_to(R)),sha256=sha(ip)),helpers=rows,helpersConsidered=27,sourceCurrent=sum(v['sourcePinCurrent'] for v in rows),outerOutputsPresent=sum('observedOuterSha256' in v for v in rows),nestedOutputsObserved=sum(len(v['nestedObservedFiles']) for v in rows),originalBinaryIdentityQualified=0,testCompilerDisposition='OUTPUT_PRESENT_OBSERVATION_ONLY_ORIGINAL_DIGEST_AND_EXPLICIT_TEST_COMPILE_TERMINAL_NOT_RECONSTRUCTED',newCompilerInvocations=0,originalTestsCompiled=0,productTestsExecuted=0,productClassesInitialized=0,actualProductProcessActions=0,archivesOrPrivateRawRead=0,newSourceProofs=0,newAcceptance=0,formalUpdated=False,whole451Accepted=False,effortRate=None,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__)))
(O/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v[k] for k in ['actualExit','helpersConsidered','sourceCurrent','outerOutputsPresent','nestedOutputsObserved','originalBinaryIdentityQualified']}))
