"""Export deputy artifacts only; no private usage or primary execution data read."""
import datetime,hashlib,json,re,subprocess,sys
from pathlib import Path
r=Path(__file__).parent; base='a39d95e172d417ae9ee6fe78a24ac29a2b8aaaa2'
def git(*args):return subprocess.check_output(['git',*args],text=True).strip()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
res=json.loads((r/'reservation.confirmed.json').read_text()); owners={x['path']:x['owner'] for x in res['files']}
changes=git('diff',base,'--name-only','--','src').splitlines(); production=[p for p in changes if '/src/main/' in p]; tests=[p for p in changes if '/src/test/' in p]
assert all(p in owners for p in production)
allowedTests=set()
for p in r.glob('*allowlist*.json'):
 d=json.loads(p.read_text())
 for field in ['tests','testAllowlist','testExecutionAllowlist']:
  for item in d.get(field,[]):
   if isinstance(item,str):allowedTests.add(item)
   elif isinstance(item,dict):allowedTests.add(item.get('path'))
# Earlier JS fixture allowlist uses exact testFile field.
for p in r.glob('*allowlist*.json'):
 d=json.loads(p.read_text());
 if 'testFile' in d:allowedTests.add(d['testFile'])
js='src/schubert-nk-web/src/test/javascript/question-input-validation.test.cjs'
assert js in (r/'P016-25.02-03-question-allowlist.json').read_text();allowedTests.add(js)
assert set(tests)<=allowedTests, set(tests)-allowedTests
(r/'final-scope-verification.json').write_text(json.dumps({'base':base,'productionCount':len(production),'testCount':len(tests),'changedProduction':[{'path':p,'owner':owners[p],'sha256':sha(p)} for p in production],'changedTests':[{'path':p,'sha256':sha(p)} for p in tests],'allChangesReserved':True,'controllerServiceSecurityWireProtocolPomLedgerChanges':[],'diffCheckExit':0,'scopeOnlyNotFormalAcceptance':True},ensure_ascii=False,indent=2)+'\n')
index={'baseCommit':base,'branch':git('branch','--show-current'),'latestImplementationCommit':git('rev-parse','HEAD'),'commits':[]}
for commit in git('rev-list','--reverse',base+'..HEAD').splitlines():
 paths=git('diff-tree','--no-commit-id','--name-only','-r',commit).splitlines(); source=[p for p in paths if p.startswith('src/')]
 index['commits'].append({'commit':commit,'subject':git('show','-s','--format=%s',commit),'sourceChanges':[{'path':p,'owner':owners.get(p),'sha256AtCommit':hashlib.sha256(subprocess.check_output(['git','show',commit+':'+p])).hexdigest()} for p in source],'reports':[p for p in paths if p.startswith('deputy-reports/')]})
(r/'commit-index-before-final-docs.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')
mapping=[('P015-07','CommonLayoutContractTest','P015-07-final-fragments.txt'),('P015-07','FiftyPaginationContractTest','common-fifty-post-fix.txt'),('P016-03','SearchDisplayContractTest','P016-03-post-fix.txt'),('P016-14','LogDisplayContractTest','P016-14-post-fix.txt'),('P016-18','QuestionInputDisplayContractTest','P016-18-post-fix.txt'),('P016-16','UserCreateDisplayContractTest','P016-16-post-fix.txt'),('P016-17','UserDetailDisplayContractTest','P016-17-post-fix.txt'),('P016-21','NotificationDetailDisplayContractTest','P016-21-fixture-final-fixture.txt'),('P016-23','QuestionDetailDisplayContractTest','P016-23-post-fix.txt'),('P016-22','QuestionListDisplayContractTest','P016-22-post-fix.txt'),('P016-20','NotificationListDisplayContractTest','P016-20-post-fix.txt'),('P016-15','UserListDisplayContractTest','P016-15-post-fix.txt'),('P016-10','AnimationWatchDisplayContractTest','P016-10-post-fix.txt'),('P016-13','MusicTrackDisplayContractTest','P016-13-post-fix.txt'),('P016-19','QuestionAcceptedDisplayContractTest','P016-19-post-fix.txt')]
trace=[]
for unit,clazz,evidence in mapping:
 path='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/view/'+clazz+'.java';methods=re.findall(r'@Test\s+void\s+(\w+)\(',Path(path).read_text());assert methods
 spec=(r/(unit+'-allowlist-expectations.json'))
 if clazz=='FiftyPaginationContractTest':spec=r/'common-fifty-allowlist-expectations.json'
 d=json.loads(spec.read_text())
 for i,method in enumerate(methods,1):
  trace.append({'testId':'PT-WD-'+unit+'-'+('FIFTY-' if clazz=='FiftyPaginationContractTest' else '')+f'{i:03}','wbs':'WBS-'+unit,'class':clazz,'method':method,'authority':d.get('expectedAuthority',d.get('authority',[])),'expectationReference':str(spec),'sourcePath':path,'currentFormattedSourceSha256':sha(path),'evidence':str(r/evidence),'evidenceSha256':sha(r/evidence),'executionClaim':'passed in recorded unit source; subsequent formatting strictly compiled, no runtime recertification of whole final source','formalAccepted':False})
(r/'test-id-requirement-evidence.json').write_text(json.dumps({'newJavaDisplayAssertions':trace,'questionJSReference':'P016-25.02-03-question-metrics.json PT-WD-QST-DIS001..003/PT-QST-JS001-B,H','existingPageProjectionReference':'P015-07-page-class-coverage.json; 8 tests class-only','notApplicable':['Direct rendering/closed-value fixtures do not execute HTTP DB/service/session/wire/operation registry. Those criteria are unmet, not covered','Pure lookup/display objects have no update retransmission; repeat rendering covered common independent contract. Actual double POST belongs primary','Browser computed layout/playback/accessibility not certified by DOM/CSS assertions'],'doNotSumDifferentSourceRunsAsFinalModulePass':True},ensure_ascii=False,indent=2)+'\n')
# Preserve historical per-leaf estimate fields as original observations, without replacing user-v3 baseline.
original=[]; wanted=set(owners.values())|{'WBS-P016-25.01','WBS-P016-25.02','WBS-P016-25.03','WBS-P016-25.04'}
for pattern in ['481*.json','484*.json']:
 for p in Path('documents/400_PGPT/470_PMO').glob(pattern):
  d=json.loads(p.read_text())
  def walk(x):
   if isinstance(x,dict):
    identity=next((v for k,v in x.items() if k in ['id','wbsId','childId'] and isinstance(v,str) and v in wanted),None)
    if identity:original.append({'source':str(p),'sha256':sha(p),'revision':d.get('revision'),'wbs':identity,'fields':{k:v for k,v in x.items() if any(t in k.lower() for t in ['cost','estimate','budget','baseline'])}})
    for v in x.values():walk(v)
   elif isinstance(x,list):
    for v in x:walk(v)
  walk(d)
metrics=[]
for p in sorted(r.glob('*.json')):
 if p.name.endswith(('-metrics.json','-read-allowlist.json')) or p.name=='P016-25.04-css-html-review.json':
  d=json.loads(p.read_text());metrics.append({'report':str(p),'sha256':sha(p),'wbs':d.get('wbs'),'beginJST':d.get('beginJST'),'endJST':d.get('endJST'),'wallElapsedSeconds':d.get('wallElapsedSeconds'),'externalJobWaitSeconds':d.get('externalJobWaitSeconds',0),'quotaBefore':d.get('quotaBefore'),'quotaAfter':d.get('quotaAfter'),'sharedSameWindowNonnegativeDeltaPp':d.get('sharedSameWindowNonnegativeDeltaPp'),'leafActualSpentPp':None,'N':None,'T':None,'wholeLeafAccepted':False})
(r/'numeric-export.json').write_text(json.dumps({'base':base,'role':'temporary-web-display-deputy','threadId':'01a12810-342a-75e1-a67b-a9d115b04bc2','responseId':None,'originalEstimateObservations':original,'userV3RemainingBaseline':{'A':9.0,'B':2.0,'C':1.25,'D':3.25,'E':17.25,'totalReference':32.75,'attachmentSha256':sha('/home/mini/.codex/attachments/b158a917-7848-449b-b841-194dad20f84d/貼り付けたテキスト.txt'),'meaning':'whole WBS reference, not deputy cost or consumption target'},'perUnit':metrics,'revisedResidualPredictionPp':None,'residualUnknownReason':'Main-owned HTTP/DB/integration/451/CHR/exit dependencies not accepted; no cost allocation inferred','publicNumericTokenUsage':None,'N':None,'T':None,'leafActualSpentPp':None,'sharedQuotaDeltaIsNotDeputyActualCost':True},ensure_ascii=False,indent=2)+'\n')
print('exported',len(production),'reserved production,',len(tests),'tests,',len(trace),'Java TestID mappings,',len(metrics),'unit snapshots')
