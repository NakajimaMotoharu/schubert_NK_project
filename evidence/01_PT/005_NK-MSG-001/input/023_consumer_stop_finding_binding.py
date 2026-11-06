"""Pin an already reviewed static counterexample; execute no Product or fixture."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
r = Path.cwd()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
head = subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
root = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/inbound/'
names = ['ApiMessagingRuntime','SyncRequestConsumers','WebLogConsumers','QuestionWorkConsumers']
paths = [root+n+'.java' for n in names]
spec = 'evidence/01_PT/005_NK-MSG-001/025_APIconsumer停止fanout不備・静的再現.md'
design = next((r/'documents/300_SS/320_メッセージング').glob('321_*.md'))
normalp = r.parent/'pgpt-runs/PG379/pg20990-outbox-required-six-main-compile-v1/manifest.safe.json'
assert sha(normalp) == '1db34d8f2ccee9fc90244bea86c3e446be0c0e010c66516a1e25c92df3426618'
normal = json.loads(normalp.read_text())
pins = {}
for name in paths+[spec,str(design.relative_to(r)),str(Path(__file__).relative_to(r))]:
    pins[name] = sha(r/name)
    assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+name])).hexdigest() == pins[name]
for name in paths:
    assert normal['begin']['inputHashes'][name] == pins[name]
assert hashlib.sha256(subprocess.check_output(['git','show','origin/main:'+str(design.relative_to(r))])).hexdigest() == sha(design)
parent = (r/paths[0]).read_text()
assert 'stopping.set(true);' in parent and 'closeGroups(groups, groupClosed);' in parent
assert 'requestStop' not in parent and 'stopDelivery' not in parent
for name in paths[1:]:
    text = (r/name).read_text()
    assert 'halted.set(true);' in text and 'halted.get()) return;' in text
out = r/'evidence/01_PT/005_NK-MSG-001/evidence/PG21910-consumer-stop-static-finding-v1'
assert not out.exists()
out.mkdir()
value = dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=head,
    productionCoreMain=normal['source'],inputHashes=pins,reviewedMainSources=4,
    existingFullTestBodyReviewComplete=False,bug='BUG-2407',ykt='YKT-2152',
    staticCounterexample='PARENT_STOP_ASYNC_CLOSE_WAIT_OTHER_GROUP_CALLBACK_ENTER',
    dynamicReproductionPerformed=False,productTestsExecuted=0,newProductTests=0,
    newMethods=0,newSourceProofs=0,newAcceptance=0,coverage=None,
    status='IMPLEMENTATION_DEFECT_STATIC_PATH_CONFIRMED_DYNAMIC_HOLD',
    formalUpdated=False,whole451Accepted=False,effortRate=None)
(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,bug=value['bug'],dynamicReproductionPerformed=False,
                     manifestSha256=sha(out/'manifest.json'))))
