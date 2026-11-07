"""Source-only cross-component QA054 binding; no Product imports or runtime operations."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
r=Path.cwd();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip();normalp=r.parent/'pgpt-runs/PG379/pg22012-web-stop-clock-six-main-compile-v1/manifest.safe.json';normal=json.loads(normalp.read_text());assert sha(normalp)=='e91d5a386618f7fc8f3fe374be760451b57bfc4d620de40a76771800d4845640' and normal['actualExit']==0
roots={'web':'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/','api':'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/'}
whole=[roots['web']+'logging/'+n+'.java' for n in ['WebRequestLogProducer','WebHttpLogKind']]+[roots['api']+'logging/WebLogIngestService.java',roots['api']+'application/log/LogQueryAuditWriter.java']
helpers=[roots['web']+n+'.java' for n in ['logging/HttpRequestLoggingValve','logging/WebRequestTrace','controller/MenuController','security/ClosedServletSecurityFilter']]+[roots['api']+'application/log/LogQueryApplicationService.java',roots['api']+'logging/RequestLogDetails.java','src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/layout/PayloadSemanticValidator.java']
pins={}
for n in whole+helpers:
 h=sha(r/n);assert h==normal['begin']['inputHashes'][n] and h==hashlib.sha256(subprocess.check_output(['git','show',head+':'+n])).hexdigest();pins[n]=h
review=r/'evidence/01_PT/005_NK-MSG-001/030_QA054メニュー・検索監査経路静的点検.md';ids=['REV-QA054-'+str(i).zfill(2) for i in range(1,9)];assert all(review.read_text().count('| '+i+' |')==1 for i in ids)
service=(r/(roots['api']+'application/log/LogQueryApplicationService.java')).read_text();persist=service[service.index('private Outcome persist('):service.index('private Rejected reject(')];assert persist.index('var snapshot = responses.read(')<persist.index('Event.SEARCH_SUCCEEDED') and 'else if (prepared instanceof Success)' in persist
producer=(r/whole[0]).read_text();assert producer.index('WebHttpLogKind.REQUEST,')<producer.index('WebHttpLogKind.MENU_VIEWED.eligible(')<producer.index('WebHttpLogKind.MENU_VIEWED,');assert 'if (!local(localLevel, json)) return false;' in producer
pins[str(review.relative_to(r))]=sha(review)
refs=[]
for n in ['evidence/01_PT/010_NK-ADM-001/087_QA054ログ検索成功監査writer単体仕様.md','evidence/01_PT/010_NK-ADM-001/088_QA054ログ検索成功監査writer単体結果.md','evidence/01_PT/015_NK-WEB-001/044_QA054メニューmarker・Trace・Controller単体仕様.md','evidence/01_PT/015_NK-WEB-001/045_QA054メニューmarker・Trace・Controller単体結果.md']:
 refs.append(dict(path=n,sha256=sha(r/n)))
out=r/'evidence/01_PT/005_NK-MSG-001/evidence/PG22074-qa054-cross-component-static-review-v1';assert not out.exists();out.mkdir();m=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=head,productionCoreMain=normal['source'],normalManifestSha256=sha(normalp),mainBodiesReviewed=whole,helperReviewScope='Exact helper methods and code spans in030; no whole Test body review inferred',inputHashes=pins,reviewIds=ids,originalOracleRefs=refs,scopeClarification='SSC337 is LogCleanup/SS341, not authority for QA054 success actions; original start preserved',canonicalCostOwner='WBS-P006-03',relatedOwners=['WBS-P006-05','WBS-P010-04'],additionalBudgetPp=0,productTestsExecuted=0,newProductTests=0,newSourceProofs=0,newAcceptance=0,coverage=None,ptExecutionExempt=False,unmeasured=['Producer encryption/outbox','API SQL duplicate and JMS ACK','Search caller snapshot/Inbox/audit transaction/rollback/concurrent replay','Actual HTTP/CHR/native/whole451'],formalUpdated=False,effortRate=None)
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,mainBodies=4,criteriaReviewedOnly=8,productTests=0,manifestSha256=sha(out/'manifest.json'))))
