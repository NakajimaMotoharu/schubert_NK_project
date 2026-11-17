"""Return the specific new ordinary error proof to the original four criteria, without acceptance."""
from pathlib import Path
import csv,datetime,hashlib,json,subprocess,sys
r=Path.cwd();sys.path[:0]=[str(r/'tools/quality'),str(r/'tools/quality/vm/050_s1')]
import pg998_metrics as metrics
from pmo_quota_binding import digest,end_fields
b=r/'evidence/01_PT/018_NK-OPS-001';d=r/'documents/400_PGPT/470_PMO/601_WBS66短期実行_20261117';ld=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
s=ld(d/'063_P00405固定投影例外通常PT開始.json');rawp=b/'evidence/PG37114-p00405-projection1-unfiltered-v1/manifest.json';raw=ld(rawp);assert raw['actualExit']==0 and raw['tests']==1 and raw['rawMissedAllCounters']==0
prior=ld(b/'evidence/PG29298-p00405-all4-original-contract-v1/manifest.json');old=ld(b/'evidence/PG29302-p00405-owner-test-qualification-v1/manifest.json');owners=old['owner'];hashes={p:sha(r/p) for p in owners}
# Compare whole source blobs against the explicit preparation Unit, not unrelated Main Core.
assert all(sha(r/p)==hashlib.sha256(subprocess.check_output(['git','show',old['source']+':'+p])).hexdigest() for p in owners)
for t in old['tests']:assert sha(r/t['path'])==t['sha256']
shared=['src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/idempotency/JdbcInboxCoordinator.java','src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/outbound/JdbcOutboxRepository.java'];sharedhash={p:sha(r/p) for p in shared}
plan=r.parent/'PMO/hourly-monitor/wbs66-20261116/58_直近20pp不足時の対象と予算判断を実行用の検収表へ渡す/922条件の受入照合.tsv';criteria=[x for x in csv.DictReader(plan.open(encoding='utf-8-sig'),delimiter='\t') if x['leaf']=='WBS-P004-05'];assert len(criteria)==4
out=b/'evidence/PG37116-p00405-current-criteria-return-v1';assert not out.exists();out.mkdir();now=datetime.datetime.now(datetime.timezone.utc).isoformat()
rows=[]
for x in criteria:
 key=x['判定ID'];detail={'WBS-P004-05/reuse':'Whole four Main and original six Test sources match source86cf preparation; unchanged RequiredColumn is not rerun; fresh new projection proof is its own Unit/run only. Whole old runtime/native success is not transferred.', 'WBS-P004-05/criterion/contract':'Five independent existing oracles remain exact. ORACLE04 fixed noarg error diagnostic now has genuine normal Test1. Actual SQL/TX/pool/UTC/ACK postconditions remain unproved or held.', 'WBS-P004-05/criterion/scope':'All four owned and two shared artifacts inventoried, no duplicate fee. Current caller/helper/driver/runtime resource closure remains unresolved for held real/backend and four-type paths.', 'WBS-P004-05/criterion/quality':'Projection whole1 passes fixed literal/no cause/no suppressed, one physical CRC, raw miss0 with natural zero branch; actual transaction/pool/full null/retry/concurrency and F02/F03 end dependencies remain incomplete.'}[key]
 rows.append(dict(id=key,sourceCore=raw['sourceCore'],actualUnitSource=raw['actualUnitSource'],decision='PARTIAL_NOT_ACCEPTED',evidence=ref(rawp),detail=detail))
(out/'criteria.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
v=dict(actualExit=0,terminalAtUTC=now,sourceCore=raw['sourceCore'],actualUnitSource=raw['actualUnitSource'],criteria=ref(out/'criteria.json'),ownedMainHashes=hashes,sharedMainHashes=sharedhash,originalSixTestHashes={x['path']:x['sha256'] for x in old['tests']},originalSourceAndWholeTestBytesUnchanged=True,newOrdinaryQualifiedMain=1,newOrdinaryTests=1,missingFixedErrorContractReduced=True,remaining=['ApiJdbcPool whole3 requires real PostgreSQL fixture/role/lifetime HOLD','JdbcSyncRequestProcessor whole transaction tests depend on held TemporaryInfrastructureException.class; no fake alternative','Actual WebLogIngestService commit/ACK whole DB/broker Test stays HOLD','Shared Inbox/Outbox current full resource/postcondition quality and all four criteria still incomplete','F02/F03 six-module/QA056 ending dependencies not accepted'],newOriginal190Accepted=0,formalUpdated=False,formalTests=1964,formalScopes=53,effortCompletionRate=None,originalP00405AuditPriceUnconsumed=.423,completedAdditionalPricePp=.3,additionalPriceTotalCompletedPp=3.45,remainingDetailBasePp='1092.098',originalSharedRuntimeSuccessTransferred=False)
(out/'manifest.json').write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,criteria=4,newAcceptance=0,proof=str(out/"manifest.json"))))
