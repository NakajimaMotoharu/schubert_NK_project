"""Finish owned metadata after real compiler success; never reruns either compiler."""
from pathlib import Path
import datetime,hashlib,json,shutil,sys,xml.etree.ElementTree as ET
R=Path.cwd();B=R/'evidence/01_PT/018_NK-OPS-001';I=B/'input';sys.path.insert(0,str(R/'tools/quality'));import pgpt_closed_host_profile as h;import pgpt_guard_signature as g;import pgpt_analysis_symbols as analysis
ld=lambda p:json.loads(p.read_text());ref=h.ref;wr=h.write_json;oldconfig=I/'2178_expiry4_corrected_closed_profile.json';c=ld(oldconfig);hashes=h.checked_inputs(c);original=R/c['slots']['prepare'];work=h.RUNS/c['privateDirs']['prepare'];oldstyle=R/c['slots']['prestyle']/'manifest.json';sm=ld(oldstyle);assert sm['actualExit']==0 and sm['inputHashes']==hashes and sm['config']==ref(oldconfig);stages={n:ld(original/(n+'-exit.safe.json')) for n in ['nullaway-compile','test-compile']}
for n,row in stages.items():
 assert row['actualExit']==0 and not row['timedOut']
 for suffix in ['stdout','stderr']:assert h.digest(original/(n+'.'+suffix))==row[suffix+'Sha256']
for n in c['mainSources']:assert h.digest(work/'src/main/java'/n.split('/src/main/java/')[1])==hashes[n]
compiler,tag=h.compiler_element();actualCompiler=ET.parse(work/'pom.xml').getroot().find('.//'+tag('plugin'));assert ET.tostring(compiler)==ET.tostring(actualCompiler)
physical=h.class_hashes(work/'target/classes');absent='dev/codex/schubert/nk/batch/repository/BatchStepResult$1.class';assert set(c['physicalClasses'])-set(physical)=={absent} and not set(physical)-set(c['physicalClasses']);assert len(physical)==21
c['physicalClasses'].remove(absent);c['standardCompilerSwitchMaps']=[];c['slots']['prestyle']='evidence/01_PT/018_NK-OPS-001/evidence/PG28714-expiry4-retained-prestyle-v1';c['slots']['prepare']='evidence/01_PT/018_NK-OPS-001/evidence/PG28716-expiry4-retained-prepare-v1';cfg=I/'2179_expiry4_actual_universe_profile.json';assert not cfg.exists();wr(cfg,c);h.validate_syntax(c);assert h.checked_inputs(c)==hashes
out=h.environment(c,'prestyle');originalStyle=oldstyle.parent
for p in originalStyle.iterdir():
 if p.is_file() and p.name!='manifest.json':shutil.copyfile(p,out/p.name)
sm.update(config=ref(cfg),retainedOriginalPrestyle=ref(oldstyle),metadataUniverseOnlyChange=True,noStyleReexecution=True);wr(out/'manifest.json',sm)
# Guard carrier was created before successful original compilation; verify, never recreate it.
carrier=work/'guard-compile-signatures.jar';signature=dict(witness=c['reviewedGuardSignature']['witness'],source=c['reviewedGuardSignature']['source'],compileCarrier=dict(path=str(carrier),sha256=h.digest(carrier)),compileClassHashes=dict(g.CLASS_SHA),runtimeClass=g.GUARD,runtimeClassSha256=g.CLASS_SHA[g.GUARD],priorPositiveGuardCrc='b5b153f7fd9d91fa');assert physical[g.GUARD+'.class']==g.CLASS_SHA[g.GUARD]
assert not (work/'component').exists();shutil.copytree(work/'target/classes',work/'component');context=analysis.create_owned_context(c,work);out=h.environment(c,'prepare')
for p in original.iterdir():
 if p.is_file():shutil.copyfile(p,out/p.name)
deps={str(p):h.digest(p) for p in [h.ANN,h.CONSOLE]};assert deps==c['preparedDependencyHashes'];cases=h.expected_cases(c);m=dict(actualExit=0,config=ref(cfg),inputHashes=hashes,dependencies=deps,toolHashes=h.tool_hashes(),physicalClassHashes=physical,testClassHashes=h.class_hashes(work/'test-classes'),expectedCases=cases,selectedClasses=sorted({x['classname'] for x in cases}),stages=stages,preliminaryStyle=ref(R/c['slots']['prestyle']/'manifest.json'),rootCompilerSha256=hashlib.sha256(ET.tostring(compiler)).hexdigest(),subsetPomSha256=h.digest(work/'pom.xml'),productTestsExecuted=0,MainCompiled=True,wholeProjectMainRebuilt=False,verifier=ref(Path(__file__).resolve()),analysisOnlyContext=context,guardSignature=signature,freshMainSourceCount=11,reusedRuntimeSignatureClassCount=1,retainedActualCompilerSuccess=dict(originalConfig=ref(oldconfig),originalCompileStreams={p.name:h.digest(p) for p in original.iterdir() if p.is_file()},noCompilerReexecution=True,metadataRemovedNonexistentSynthetic=absent,actualPhysicalClasses=21));wr(out/'manifest.json',m);g.validate_prepared(c,m,work);analysis.validate_prepared(c,m,work);print(json.dumps(dict(actualExit=0,retainedRootCompile=0,retainedWholeTestCompile=0,physicalClasses=21,compilerReexecuted=False,ProductPT=0)))
