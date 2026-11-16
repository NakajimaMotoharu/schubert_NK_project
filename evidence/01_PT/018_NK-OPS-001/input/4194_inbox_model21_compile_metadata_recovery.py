"""Recover metadata from the successful original Root/Test compile; do not recompile or overwrite evidence."""
from pathlib import Path
import datetime,json,shutil,xml.etree.ElementTree as ET
import pgpt_closed_host_profile as h
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';i=b/'input';oldp=i/'4188_inbox_model21_profile.json';old=h.read_json(oldp);cfg=i/'4188b_inbox_model21_actual15_profile.json';c=dict(old);phantom='dev/codex/schubert/nk/api/idempotency/InboxException$1.class';assert phantom in old['physicalClasses'];c['physicalClasses']=[n for n in old['physicalClasses'] if n!=phantom];c['targetClasses']=[n for n in old['targetClasses'] if n!=phantom[:-6]];c['slots']=dict(old['slots']);c['slots']['prestyle']=str((b/'evidence/PG35705-inbox-model21-prestyle-rebind-v1').relative_to(r));assert len(c['physicalClasses'])==15 and len(c['mainSources'])==14
# Exact source/compiler/dependency inputs are unchanged; only nonexistent predicted name and style receipt slot differ.
assert all(c[k]==old[k] for k in c if k not in ['physicalClasses','targetClasses','slots']);h.write_json(cfg,c);h.validate_syntax(c);hashes=h.checked_inputs(c);prepath=r/old['slots']['prestyle']/'manifest.json';pre=h.read_json(prepath);assert pre['actualExit']==0 and pre['config']==h.ref(oldp) and pre['inputHashes']==hashes
out=r/c['slots']['prestyle'];out.mkdir()
for p in prepath.parent.iterdir():
 if p.name!='manifest.json':assert p.is_file();shutil.copyfile(p,out/p.name)
newpre=dict(pre);newpre.update(config=h.ref(cfg),originalPreliminaryStyle=h.ref(prepath),sameSourceStyleReceiptRebound=True,onlyNonexistentPhysicalPredictionChanged=True,styleExecutionsRepeated=0);h.write_json(out/'manifest.json',newpre)
w=h.RUNS/c['privateDirs']['prepare'];physical=h.class_hashes(w/'target/classes');assert set(physical)==set(c['physicalClasses'])
for n in physical:h.relative_name(n)
assert not (w/'component').exists() and not (r/c['slots']['prepare']/'manifest.json').exists();stages={}
for stage in ['nullaway-compile','test-compile']:
 sp=r/old['slots']['prepare']/(stage+'-exit.safe.json');s=h.read_json(sp);assert s['actualExit']==0 and not s['timedOut']
 for label in ['stdout','stderr']:assert h.digest(sp.parent/(stage+'.'+label))==s[label+'Sha256']
 if stage=='nullaway-compile':assert s['cwd']==str(w) and s['command'][0]==str(h.MAVEN) and s['command'][-1]=='compile'
 else:assert s['cwd']==str(r) and s['command'][0]==str(h.JAVAC) and s['command'][-len(c['testSources']):]==[str(r/x['path']) for x in c['testSources']]
 stages[stage]=s
for name in c['mainSources']:
 copied=w/'src/main/java'/name.split('/src/main/java/')[1];assert h.digest(copied)==hashes[name]
compiler,tag=h.compiler_element();actual=ET.parse(w/'pom.xml').getroot().find('.//'+tag('plugin'));assert ET.tostring(compiler)==ET.tostring(actual)
deps={str(h.ANN):h.digest(h.ANN),str(h.CONSOLE):h.digest(h.CONSOLE)};assert c['sdkJars']==[];shutil.copytree(w/'target/classes',w/'component');m=dict(actualExit=0,config=h.ref(cfg),inputHashes=hashes,dependencies=deps,toolHashes=h.tool_hashes(),physicalClassHashes=physical,testClassHashes=h.class_hashes(w/'test-classes'),expectedCases=h.expected_cases(c),selectedClasses=sorted({x['classname'] for x in h.expected_cases(c)}),stages=stages,preliminaryStyle=h.ref(out/'manifest.json'),rootCompilerSha256=__import__('hashlib').sha256(ET.tostring(compiler)).hexdigest(),subsetPomSha256=h.digest(w/'pom.xml'),productTestsExecuted=0,MainCompiled=True,wholeProjectMainRebuilt=False,verifier=h.ref(Path(__file__).resolve()),unstartedProcess=None,analysisOnlyContext=None,guardSignature=None,freshMainSourceCount=14,reusedRuntimeSignatureClassCount=0,originalCompileRecoveredWithoutReplay=True,originalFailedProfile=h.ref(oldp),onlyMissingManifestRecovered=True,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat());h.write_json(r/c['slots']['prepare']/'manifest.json',m)
# Correct only source/wrapper predictions for subsequent use; preserve old snapshots in the defect evidence.
e=b/'evidence/PG35703-physical-universe-prediction-defect-v1'
for file in ['4187_inbox_model21_source_profile.py','4190_inbox_model21_post_join.py','4191_inbox_model21_unfiltered.py']:
 p=i/file;t=p.read_text();(e/(file+'.before.txt')).open('x').write(t)
 if file.startswith('4187'):t=t.replace(",'dev/codex/schubert/nk/api/idempotency/InboxException$1'",'').replace('physical=16','physical=15')
 else:
  t=t.replace('4188_inbox_model21_profile.json','4188b_inbox_model21_actual15_profile.json').replace("p['physicalClasses']==16","p['physicalClasses']==15").replace("p['positiveMainCrc']==16","p['positiveMainCrc']==15").replace('len(physical)==16','len(physical)==15').replace('physical16OnlyNoProtocolJar','physical15OnlyNoProtocolJar').replace('physical=16,positiveCrc=16','physical=15,positiveCrc=15').replace('len(names)==len(set(names))==16','len(names)==len(set(names))==15').replace('exact16 permitted','exact15 permitted').replace('len(target_names)==16','len(target_names)==15').replace('own14Main16PhysicalRawFour100','own14Main15PhysicalRawFour100').replace('all16ScopeAccepted','all15ScopeAccepted')
 p.write_text(t)
h.write_json(e/'compile-recovery.json',dict(actualExit=0,config=h.ref(cfg),prepare=h.ref(r/c['slots']['prepare']/'manifest.json'),originalCompileExecutionsRepeated=0,physical15Complete=True,nonexistentPredictionOnlyRemoved=True,whole451Accepted=False));print(json.dumps(dict(actualExit=0,physical=15,rootMain=14,tests=21,compileReplay=0,onlyMissingPrepareManifestRecovered=True)))
