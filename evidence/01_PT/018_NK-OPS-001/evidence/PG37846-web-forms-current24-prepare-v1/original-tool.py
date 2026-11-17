"""Reuse exact current7Main/12bytes qualified Root NullAway/MaxLow; compile only the three needed Tests."""
from pathlib import Path
import datetime,hashlib,json,shutil,zipfile
import pgpt_closed_host_profile as policy
import pg9666_pagination_static as steps
r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001';tc=r.parent/'toolchain';runs=r.parent/'pgpt-runs/PG379';ld=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
closure=ld(b/'evidence/PG37844-web-forms-current24-source-v1/manifest.json');main=closure['mainSources'];tests=[x['path'] for x in closure['testSources']];assert len(main)==7 and len(tests)==3 and all(sha(r/n)==h for n,h in closure['sourceHashes'].items())
unionpath=b/'evidence/PG37782-pure-protocol-web-maxlow-prepare-v1/manifest.json';union=ld(unionpath);assert union['actualExit']==0
stems=[n.split('/src/main/java/')[1][:-5] for n in main];selected={n:h for n,h in union['physicalClassHashes'].items() if any(n==s+'.class' or n.startswith(s+'$') for s in stems)};assert len(selected)==12
for n in main:assert union['sourceHashes'][n]==sha(r/n)
compile_refs=[];covered=set()
for dirname in ['PG37692-web-enum-eight-prepare-v1','PG37758-web-trace-current24-prepare-v1']:
    file=b/'evidence'/dirname/'manifest.json';p=ld(file);stage=p['stages']['nullaway-compile'];assert p['actualExit']==0 and stage['actualExit']==0 and not stage['timedOut']
    assert p['inputHashes']['pom.xml']==sha(r/'pom.xml') and p['inputHashes']['src/schubert-nk-web/pom.xml']==sha(r/'src/schubert-nk-web/pom.xml')
    assert p['compilerConfiguration']=='EXACT_ROOT_RELEASE25_ERRORPRONE2500_NULLAWAY0141_NO_PROC_NONE_FOR_MAIN'
    matching=[n for n in main if n in p['apiMainSources']];assert all(p['inputHashes'][n]==sha(r/n) for n in matching);covered.update(matching);compile_refs.append(dict(prepare=ref(file),matchedCurrentMain=matching,originalCompileStage=stage))
assert covered==set(main)
protofile=b/'evidence/PG37688-web-enum-current-protocol176-v1/manifest.json';proto=ld(protofile);jar=Path(proto['jar']['path']);assert sha(jar)==proto['jar']['sha256'] and len(proto['physicalClassHashes'])==176
assert all(sha(r/n)==h for n,h in proto['inputHashes'].items())
work=runs/'pg37846-web-forms-current24-v1';out=b/'evidence/PG37846-web-forms-current24-prepare-v1';assert not work.exists() and not out.exists();work.mkdir();out.mkdir();component=work/'component';component.mkdir();physical={}
for n,h in selected.items():
    policy.relative_name(n);row=union['byteInputs'][n];source=Path(row['path']);assert sha(source)==h;dest=component/n;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest);physical[n]=h
with zipfile.ZipFile(jar) as archive:
    for n,h in proto['physicalClassHashes'].items():
        policy.relative_name(n);assert n not in physical;raw=archive.read(n);assert hashlib.sha256(raw).hexdigest()==h;dest=component/n;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);physical[n]=h
assert len(physical)==188 and all(union['physicalClassHashes'][n]==h for n,h in physical.items())
ann=tc/'m2/repository/org/jspecify/jspecify/1.0.1/jspecify-1.0.1.jar';console=tc/'junit-platform-console-standalone-1.13.4.jar';deps={str(n):sha(n) for n in [jar,ann,console]};assert union['dependencies'][str(ann)]==sha(ann)
classes=work/'test-classes';classes.mkdir();steps.SLOT=out
stage=steps.step('test-compile',[str(tc/'jdk-25.0.4/bin/javac'),'--release','25','-g','-proc:none','-implicit:none','-encoding','UTF-8','-Xlint:all','-Werror','-cp',':'.join([str(component),*deps]),'-d',str(classes),*[str(r/n) for n in tests]],r)
assert stage['actualExit']==0 and not stage['timedOut']
for file in classes.rglob('*.class'):policy.relative_name(str(file.relative_to(classes)))
inputs={n:sha(r/n) for n in main+tests+['pom.xml','src/schubert-nk-web/pom.xml']};inputs.update(proto['inputHashes'])
v=dict(actualExit=0,terminalAtUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),work=str(work),inputHashes=inputs,apiMainSources=main,apiTestSources=tests,dependencies=deps,physicalClassHashes=physical,mainClassHashes=selected,testClassHashes={str(n.relative_to(classes)):sha(n) for n in classes.rglob('*.class')},expectedCases=closure['expectedCases'],expectedTests=24,newDefinitions=0,necessaryPriorDefinitions=24,sourceCore='a013a6d676454082de3c59bc199e87f37fefe159',stages={'test-compile':stage},originalMainNullAwayProofs=compile_refs,allCurrentMainSourcesCoveredByOriginalRootNullAway=True,MainCompileReplayed=False,all188ByteCurrent251Exact=True,currentProto=ref(protofile),current251=ref(unionpath),productTestsExecuted=0,actualHeldClassBinaryAccess=False,newAcceptance=0,formalUpdated=False)
(out/'manifest.json').write_text(json.dumps(v,indent=2)+'\n');print(dict(actualExit=0,main7=7,mainPhysical12=12,allPhysical188=188,expectedTests=24,MainCompileReplayed=False,testCompile=0))
