"""Freeze exact changed Main and retained whole original9 plus SIGN010 in a closed profile."""
from pathlib import Path
import datetime,hashlib,json,subprocess
import pgpt_closed_host_profile as h
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ld=lambda p:json.loads(p.read_text());ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p));write=lambda p,v:p.open('x').write(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
c=ld(i/'2220_signature9_closed_profile.json');test=c['testSources'][0]['path'];old=subprocess.check_output(['git','show','58ade749adfe6c34cf5f2cd45a4bc9ab71c29b0a:'+test],text=True);now=(r/test).read_text();marker='  /** SIGN010/SSC419:';prefix=now[:now.index(marker)].replace('import static org.junit.jupiter.api.Assertions.assertNotSame;\n','');assert prefix.rstrip()==old.rsplit('}',1)[0].rstrip()
assert len(h.expected_cases(dict(c,testSources=[dict(path=test,tests=10)],expectedTests=10)))==10
for path in c['mainSources']:h.relative_name(path)
for name in c['physicalClasses']:h.relative_name(name)
e=b/'evidence/PG33761-ssc419-signature10-source-closure-v1';assert e.exists()
proof=dict(actualExit=0,atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),productionCoreMain='9fdf9bea361a4450401d9a197785bea26e33bcf2',source='310e8986061d980a02287d2401ff21ffefd916ca',mainInputHashes={path:sha(r/path) for path in c['mainSources']},testInputHashes={test:sha(r/test)},oldWhole9BodiesExactPrefix=True,newDefinition=1,expectedWholeTests=10,sourceScope='FixedJDKpublicRFC verification and pure StorageIoException only',oldQualificationNotTransferred=True,actualBackendActions=0)
saved=ld(e/'manifest.json');assert all(saved[k]==v for k,v in proof.items() if k!='atUTC');proof=saved
c.update(id='PG33770-SSC419-SIGNATURE10',productionCoreMain=proof['productionCoreMain'],testSources=[dict(path=test,tests=10)],expectedTests=10,newTestDefinitions=1,oracleSpecs=[ref(b/'4277_SSC419_署名clone取得直後保護・通常全十仕様.md')],closureProofs=[ref(e/'manifest.json')])
c['slots']={phase:str((b/'evidence'/f'PG{num}-ssc419-signature10-{phase}-v1').relative_to(r)) for phase,num in [('prestyle',33762),('prepare',33764),('static',33766),('preflight',33768),('unit',33770),('post',33772)]};c['privateDirs']=dict(prepare='pg33764-ssc419-signature10-prepare-v1',unit='pg33770-ssc419-signature10-unit-v1')
assert c['costWbsLeafIds']==['WBS-F03'] and c['costBoundary']=='ADDITIONAL_QUALIFICATION_NO_ORIGINAL_COST_REASSIGNMENT'
# Profile classification is quality-only; actual group cost remains the single P01802 event5415, no new fee/event.
p=i/'3480_ssc419_signature10_profile.json';h.checked_inputs(c);write(p,c);print(json.dumps(dict(actualExit=0,source=proof['source'],Main2=2,whole10=10,newDefinitions=1,oldWhole9Unchanged=True)))
