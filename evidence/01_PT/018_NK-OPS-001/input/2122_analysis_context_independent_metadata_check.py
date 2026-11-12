from pathlib import Path
import copy,datetime,hashlib,json,sys,xml.etree.ElementTree as ET,zipfile
R=Path.cwd();sys.path.insert(0,str(R/'tools/quality'));import pgpt_analysis_symbols as a;import pgpt_closed_host_profile as h
B=R/'evidence/01_PT/018_NK-OPS-001';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(R)),sha256=sha(p));wr=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n');cp=B/'input/2121_log_whole21_analysis_context_profile.json';c=ld(cp);m=ld(R/c['slots']['prepare']/'manifest.json');st=ld(R/c['slots']['static']/'manifest.json');W=h.RUNS/c['privateDirs']['prepare'];checks=[]
def valid(name,fn):fn();checks.append(dict(id=name,result='ACCEPT'))
def invalid(name,fn):
 try:fn()
 except ValueError:checks.append(dict(id=name,result='REJECT'));return
 raise AssertionError(name)
valid('EXACT_PROFILE_METADATA',lambda:h.validate_syntax(c));valid('PUBLIC_SOURCE_AND_SYMBOL_PROVENANCE',lambda:a.checked(c));valid('EXACT_OWN_ANALYSIS_CARRIER_NO_RUNTIME',lambda:a.validate_prepared(c,m,W))
for name,change in [('MISSING_GUARD_MODE',lambda v:v.pop('reviewedGuardSignature')),('EXTRA_CONTEXT_OPTION',lambda v:v['reviewedAnalysisOnlyContext'].update(allowRuntime=True)),('WRONG_WITNESS_PATH',lambda v:v['reviewedAnalysisOnlyContext']['witness'].update(path='evidence/other.json')),('UNPINNED_WITNESS',lambda v:v.update(closureProofs=[])),('ANALYSIS_CLASS_IN_RUNTIME',lambda v:v['physicalClasses'].append(a.CHILD+'.class')),('MISSING_INIT_FENCE',lambda v:v['forbiddenInitializedClasses'].remove(a.CHILD+'$MaintenanceParent')),('NATIVE_SOURCE_COMPILE_UNIT',lambda v:v['mainSources'].append(a.SOURCE_PATHS[0]))]:
 v=copy.deepcopy(c);change(v);invalid(name,lambda v=v:a.syntax(v))
for name,change in [('WRONG_CARRIER_CLASS_HASH',lambda v:v['analysisOnlyContext']['classes'].update({a.CHILD:'0'*64})),('RUNTIME_DEPENDENCY_INJECTION',lambda v:v['dependencies'].update({str(W/'analysis-only-six-symbols.jar'):'0'*64})),('RUNTIME_CLASS_INJECTION',lambda v:v['physicalClassHashes'].update({a.CHILD+'.class':'0'*64})),('RUNTIME_PURPOSE_INJECTION',lambda v:v['analysisOnlyContext'].update(purpose='RUNTIME')),('CARRIER_PATH_ALIAS',lambda v:v['analysisOnlyContext']['carrier'].update(path='/tmp/alias.jar')),('CARRIER_HASH_DRIFT',lambda v:v['analysisOnlyContext']['carrier'].update(sha256='0'*64))]:
 v=copy.deepcopy(m);change(v);invalid(name,lambda v=v:a.validate_prepared(c,v,W))
plain=ld(B/'input/2103_jdbc_knownpair8_profile.json');invalid('IMPLICIT_CONTEXT_WITHOUT_OPTION',lambda:a.validate_prepared(plain,m,W));legacy=[]
for n in ['2045_batch_run2_profile.json','2075_backup_profile4_profile.json','2084_cleanup_values14_profile.json','2103_jdbc_knownpair8_profile.json']:
 p=B/'input'/n
 if p.exists():h.validate_syntax(ld(p));legacy.append(ref(p))
assert all(st['spotbugs'][x]==0 for x in ['bugs','missing','errors']);assert st['newMissingClassNames']==[] and st['originalSuccessfulCompilerAndPmdCsGjfPreserved'];assert st['analysisOnlyContext']==m['analysisOnlyContext'];carrier=Path(st['analysisOnlyContext']['carrier']['path']);assert carrier==W/'analysis-only-six-symbols.jar' and sha(carrier)==st['analysisOnlyContext']['carrier']['sha256']
with zipfile.ZipFile(carrier) as z:
 assert len(z.namelist())==6 and set(z.namelist())=={n+'.class' for n in a.NAMES}
 for n in a.NAMES:assert hashlib.sha256(z.read(n+'.class')).hexdigest()==m['analysisOnlyContext']['classes'][n]
# Root compiler POM remains unchanged; analyzer POM adds exactly one data dependency.
ns={'m':'http://maven.apache.org/POM/4.0.0'};original=ET.parse(W/'pom.xml').getroot();analysis=ET.parse(st['analysisPom']['path']).getroot();assert sha(Path(st['analysisPom']['path']))==st['analysisPom']['sha256'];oldDeps=original.find('m:dependencies',ns);newDeps=analysis.find('m:dependencies',ns);assert len(newDeps)==len(oldDeps)+1
for left,right in zip(oldDeps,list(newDeps)[:-1]):assert ET.tostring(left)==ET.tostring(right)
last=newDeps[-1];assert last.findtext('m:systemPath',namespaces=ns)==str(carrier) and last.findtext('m:scope',namespaces=ns)=='system';assert ET.tostring(original.find('.//m:plugin',ns))==ET.tostring(analysis.find('.//m:plugin',ns));assert h.class_hashes(W/'target/classes')==m['physicalClassHashes']==h.class_hashes(W/'component');assert not {n+'.class' for n in a.NAMES}&set(m['physicalClassHashes']);assert str(carrier) not in m['dependencies'];assert len(m['physicalClassHashes'])==23 and len(m['expectedCases'])==21
previous=ld(R/st['originalStatic']['path']);retained=[]
for label in ['pmd','checkstyle','format']:
 assert st['stages'][label]==previous['stages'][label]
 for stream in ['stdout','stderr']:assert sha((R/c['slots']['static'])/(label+'.'+stream))==st['stages'][label][stream+'Sha256']
 retained.append(label)
assert len(st['rawFindings'])==69 and st['rawFindings']==previous['rawFindings'];assert st['fullRootRulesetSha256']==previous['fullRootRulesetSha256'];assert not (h.RUNS/c['privateDirs']['unit']).exists();O=B/'evidence/PG28436-analysis-only-context-independent-metadata-v1';assert not O.exists();O.mkdir();v=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),cases=len(checks),positive=3,negative=len(checks)-3,checks=checks,legacyProfileSyntaxOnly=legacy,profile=ref(cp),prepared=ref(R/c['slots']['prepare']/'manifest.json'),static=ref(R/c['slots']['static']/'manifest.json'),allSixClassHashesAndCarrierEntriesIndependent=True,rootCompilerFragmentUnchanged=True,analyzerPomOnlyOneAnalysisDependencyAdded=True,originalRootCompileAndTestCompileReexecuted=False,retainedOriginalPmdCsGjf=retained,sourceInputPhysical23AndTest21Unchanged=True,spotbugsBugsMissingErrors=0,rawPmdFindingsStillUnclassified=69,whole21NeverStarted=True,productTestsExecuted=0,newAcceptance=0,whole451Accepted=False,actualRootNativeOrHeldOperations=0,verifier=ref(Path(__file__).resolve()));wr(O/'manifest.json',v);print(json.dumps(dict(actualExit=0,metadataCases=len(checks),spotbugsMissing=0,rawPmdStill69=True,whole21NotRun=True,manifest=ref(O/'manifest.json'))))
