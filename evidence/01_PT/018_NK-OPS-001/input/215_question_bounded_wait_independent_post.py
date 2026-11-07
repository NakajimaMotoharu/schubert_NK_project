"""Source-only bounded-Future repair verification and twenty-site static rebinding; no original Test execution."""
from pathlib import Path
import collections
import datetime
import hashlib
import json
import re
import subprocess
import pg9666_pagination_static as c
R=Path(__file__).resolve().parents[4];RUNS=R.parent/'pgpt-runs/PG379';P=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22488-question-bounded-wait-static-v1';OUT=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22492-question-bounded-wait-independent-v1';SLOT=RUNS/'pg22492-question-bounded-wait-independent-v1'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads(Path(p).read_bytes())
TOKEN=re.compile(r'(?P<comment>//[^\n]*|/\*[\s\S]*?\*/)|"""[\s\S]*?"""|"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|\w+|[^\s]')
def tokens(s):return [m.group() for m in TOKEN.finditer(s) if not m.group('comment')]
def exact_fix(before,after):return before.count('job.get()')==1 and tokens(before.replace('job.get()','job.get(10, TimeUnit.SECONDS)'))==tokens(after)
def main():
    assert not OUT.exists() and not SLOT.exists();m=load(P/'manifest.json');assert sha(P/'manifest.json')=='3533e46bfe18e41fa7164c7f0247cff66255f9890d6b9225b2ec4d0ba643af89' and m['actualExit']==0 and m['source']=='a9ac8f7890a210a3e2032b9d6a013d3a5a1dfe24' and m['checkedFiles']==1;begin=m['begin'];name=next(iter(begin['inputHashes']));assert name=='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/QuestionControllerTest.java';assert sha(R/name)==begin['inputHashes'][name]==hashlib.sha256(subprocess.check_output(['git','show',m['source']+':'+name],cwd=R)).hexdigest()
    for path,h in {**begin['toolHashes'],**begin['dependencies']}.items():assert sha(path)==h
    for path,h in m['files'].items():assert sha(P/path)==h
    for label,stage in m['stages'].items():
        assert stage==load(P/(label+'-exit.safe.json')) and not stage['timedOut']
        for stream in ['stdout','stderr']:assert sha(P/(label+'.'+stream))==stage[stream+'Sha256']
    assert m['reports']['pmd']['raw']==20 and m['reports']['checkstyle']['raw']==0 and m['stages']['pmd']['actualExit']==4 and m['stages']['checkstyle']['actualExit']==0 and all(not x['processingErrors'] for x in m['reports'].values())
    original=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22482-question-unbounded-original-v1';o=load(original/'manifest.json');oldfile=original/'QuestionControllerTest.java';assert sha(oldfile)==o['sha256'];before=oldfile.read_text();after=(R/name).read_text();assert exact_fix(before,after);assert 'future.get(10, TimeUnit.SECONDS)' in before and 'job.get()' not in after
    negative=[before,after.replace('job.get(10, TimeUnit.SECONDS)','job.get(11, TimeUnit.SECONDS)'),after+'\nclass UnexpectedChange {}\n'];assert all(not exact_fix(before,bad) for bad in negative)
    oldbase=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22382-ordinary85-test-static-v1';oldraw=[x for x in load(oldbase/'unclassified-sites.json') if x['path']==name];newraw=load(P/'unclassified-sites.json');assert len(oldraw)==len(newraw)==20;positions={'beginline','endline','begincolumn','endcolumn'};bindings=[]
    for old,new in zip(oldraw,newraw):
        assert new['path']==name and new['sourceSha256']==sha(R/name);assert {k:v for k,v in old['attributes'].items() if k not in positions}=={k:v for k,v in new['attributes'].items() if k not in positions};assert old['message']==new['message'];bindings.append(dict(originalOrdinal=old['ordinal'],rule=new['attributes']['rule'],currentAttributes=new['attributes'],priorReasonRetainedByExactOtherTokens=True,currentSourceSha256=sha(R/name)))
    assert collections.Counter(x['rule'] for x in bindings)=={'DoNotUseThreads':4,'UseProperClassLoader':3,'CloseResource':1,'AvoidUsingVolatile':12}
    prior=R/'evidence/01_PT/010_NK-ADM-001/evidence/PG22444-user-audit-static-source-rebinding-v1/manifest.json';rb=load(prior);assert len(rb['inputHashes'])==85
    for path,h in rb['inputHashes'].items():
        assert not any(x in path for x in ['RootFailedStart','SnapshotKeyCloseWitness','pg9892_'])
        if path!=name:assert sha(R/path)==h
    toolpost=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22474-question-volatile12-independent-v1/manifest.json';assert sha(toolpost)=='5871872955bce57c6d9e48d0090df72ee56cf694f663f73e497853f6503d7125';old=load(toolpost);tool=R/old['tool']['path'];owned=RUNS/'pg22474-question-volatile12-independent-v1';assert sha(tool)==old['tool']['sha256']==sha(owned/'source/QuestionFixtureControlAstCheck.java');assert old['stages']['tool-javac']['actualExit']==0;classes={p.name:sha(p) for p in (owned/'classes').glob('*.class')};assert set(classes)=={'QuestionFixtureControlAstCheck.class','QuestionFixtureControlAstCheck$1.class'}
    SLOT.mkdir();c.SLOT=SLOT;stage=c.step('parse',[str(R.parent/'toolchain/jdk-25.0.4/bin/java'),'-cp',str(owned/'classes'),'QuestionFixtureControlAstCheck',str(R),name],R,timeout=120);assert stage['actualExit']==0 and not stage['timedOut'];ast=[x.split('\t') for x in (SLOT/'parse.stdout').read_text().splitlines()];oldast=[x.split('\t') for x in (toolpost.parent/'parse.stdout').read_text().splitlines()];assert not any(x[0]=='UNBOUNDED_GET' for x in ast)
    # All field/control write semantics are unchanged; only source positions may move after formatting.
    semantic=lambda rows,kind:collections.Counter(tuple(x[:4]+x[5:]) if kind=='FIELD' else tuple(x[:5]+x[6:]) for x in rows if x[0]==kind)
    assert semantic(ast,'FIELD')==semantic(oldast,'FIELD');assert semantic(ast,'WRITE')==semantic(oldast,'WRITE');assert sum(x[0]=='FIELD' for x in ast)==12 and sum(x[0]=='WRITE' for x in ast)==49 and not any(x[0]=='RMW' for x in ast)
    fmt=load(RUNS/'pg22484-question-bounded-wait-format-v1/manifest.json');assert fmt['actualExit']==0 and '--skip-reflowing-long-strings' in fmt['stage']['command'] and fmt['testSha256']==sha(R/name)
    correction=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22490-question-static-count-label-original-v1/manifest.json';co=load(correction);assert co['originalCountLabel']==19 and co['correctCountLabel']==20 and not co['sourceScopeChanged'];spec=R/'evidence/01_PT/018_NK-OPS-001/3666_BUG2432_Question並行wait有限化PG・静的確認仕様.md';assert '全20指摘=thread4/loader3/CloseResource1/volatile12' in spec.read_text();assert classes=={p.name:sha(p) for p in (owned/'classes').glob('*.class')}
    OUT.mkdir();files={}
    for file in ['parse.stdout','parse.stderr','parse-exit.safe.json']:(OUT/file).write_bytes((SLOT/file).read_bytes());files[file]=sha(OUT/file)
    (OUT/'twenty-site-rebindings.json').write_text(json.dumps(bindings,ensure_ascii=False,indent=2)+'\n');files['twenty-site-rebindings.json']=sha(OUT/'twenty-site-rebindings.json')
    result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=m['source'],productionCoreMain=begin['productionCoreMain'],testPath=name,testSha256=sha(R/name),originalTestManifest=dict(path=str((original/'manifest.json').relative_to(R)),sha256=sha(original/'manifest.json')),staticManifest=dict(path=str((P/'manifest.json').relative_to(R)),sha256=sha(P/'manifest.json')),singleFutureCallChanged=True,allOtherJavaTokensUnchanged=True,negativeTokenGuards=len(negative),originalTargetUnboundedFutureCalls=1,currentTargetUnboundedFutureCalls=0,waitMeasurementScope="FIXED_JOB_GET_AND_KNOWN_JOB_FUTURE_AST_RECEIVERS_OTHER_WAITS_NOT_AUDITED",controlFieldsUnchanged=12,externalControlWritesUnchanged=47,bareMonotoneWritesUnchanged=2,otherTestSourcesUnchanged=84,currentSubsetRaw=346,currentSubsetClassified=283,currentSubsetUnclassified=63,requalifiedStaticSites=20,newIndividualClassifications=0,sourcePgFixImplemented=True,dynamicTestStatus='NOT_RUN_HOLD',bug='BUG-2432',bugState='SOURCE_FIXED_STATIC_CHECKED_PT_NOT_RUN_HOLD',ykt='YKT-2177',yktState='OPEN_LATERAL_FUTURE_WAITS_NOT_YET_AUDITED',countLabelBug='BUG-2433',countLabelYkt='YKT-2178',countLabelCorrectionVerified=True,productTestsExecuted=0,newProductTests=0,newSourceProofs=0,newAcceptance=0,wholeF03Accepted=False,whole451Accepted=False,effortRate=None,stage=stage,files=files,reusedParseTool=dict(path=str(tool.relative_to(R)),sha256=sha(tool),physical=classes),verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(__file__),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip()))
    (OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,sourcePgFixed=True,dynamicTestStatus='NOT_RUN_HOLD',requalifiedStaticSites=20,manifestSha256=sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
