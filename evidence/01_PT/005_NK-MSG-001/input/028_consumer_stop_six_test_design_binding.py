"""Read-only binding of existing Test designs; never import a Product or Test module."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess
r = Path.cwd()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
head = subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
root = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/inbound/'
names = ['ApiMessagingRuntimeTest','SyncRequestConsumersTest','WebLogConsumersTest','QuestionWorkConsumersTest']
pins, cases = {}, {}
for name, expected in zip(names,[10,6,6,6]):
    n = root+name+'.java'
    pins[n] = sha(r/n)
    assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+n])).hexdigest() == pins[n]
    methods = re.findall(r'@Test\s+void\s+(\w+)\(', (r/n).read_text())
    assert len(methods) == len(set(methods)) == expected
    cases[n] = methods
helper = root+'InternalEventListenerTest.java'
pins[helper] = sha(r/helper)
assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+helper])).hexdigest() == pins[helper]
spec = 'evidence/01_PT/005_NK-MSG-001/026_APIconsumer停止fanout是正・独立PT仕様.md'
review = 'evidence/01_PT/005_NK-MSG-001/028_停止fanout六PT設計レビュー・既28method対応.md'
ids = ['PT-JMS-STOP-GROUP'+str(i).zfill(3) for i in range(1,7)]
for n in [spec,review,str(Path(__file__).relative_to(r))]:
    pins[n] = sha(r/n)
    assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+n])).hexdigest() == pins[n]
for n in [spec,review]:
    assert re.findall(r'^\| (PT-JMS-STOP-GROUP\d{3}) \|',(r/n).read_text(),re.M) == ids
normalp = r.parent/'pgpt-runs/PG379/pg21922-consumer-stop-six-main-compile-v1/manifest.safe.json'
assert sha(normalp) == 'e925b4c24e0eff9e70f7b3fad0b595d80e90f1a444c87329215d6e4b3d5d8d1f'
normal = json.loads(normalp.read_text())
mainroot = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/inbound/'
for name in [n.removesuffix('Test') for n in names]+['InboundConsumerGroup']:
    n = mainroot+name+'.java'
    pins[n] = sha(r/n)
    assert pins[n] == normal['begin']['inputHashes'][n]
out = r/'evidence/01_PT/005_NK-MSG-001/evidence/PG21954-stop-six-existing28-design-review-v1'
assert not out.exists()
out.mkdir()
value = dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=head,
    productionCoreMain=normal['source'],inputHashes=pins,existingTestMethodsDesignOnly=cases,
    existingTestDesignMethodCount=28,newPendingTestIds=ids,
    newTestStatuses={n:'NOT_RUN_HOLD' for n in ids},
    helperBodyReview=dict(path=helper,methods=['queue','sendEvent','eventWire','ascii','start'],wholeTestClassReviewed=False),
    oldTransportFixtureNotTypedBusinessProof=True,
    productTestsExecuted=0,newProductTests=0,newMethods=0,newSourceProofs=0,newAcceptance=0,
    coverage=None,bugsRemainOpen=['BUG-2407','YKT-2152'],ptExecutionExempt=False,
    whole451Accepted=False,formalUpdated=False,effortRate=None)
(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,existingMethodsReviewedOnly=28,pendingTests=6,
                     productTestsExecuted=0,manifestSha256=sha(out/'manifest.json'))))
