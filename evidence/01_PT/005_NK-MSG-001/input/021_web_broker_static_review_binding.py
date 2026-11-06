"""Bind a read-only design review; do not initialize or execute any Product class."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess

r = Path.cwd()
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
load = lambda p: json.loads(p.read_text())
head = subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
main = 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/messaging/WebBrokerContexts.java'
root = 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/'
tests = [root+'web/messaging/'+n+'.java' for n in [
    'WebBrokerContextsTest','WebBrokerFactoryOwnershipTest','BrokerGraph334Test',
    'WebFactoryNativeRetentionTest']]+[root+'api/file/WebBrokerContextsCredentialTest.java']
docs = [r/'evidence/01_PT/005_NK-MSG-001'/n for n in [
    '021_WebBroker所有全契約静的レビュー仕様.md','022_WebBroker所有全契約静的レビュー結果.md']]
designs = list((r/'documents/300_SS/320_メッセージング').glob('321_*.md'))
designs += list((r/'documents/300_SS/340_batch・基盤').glob('343_*.md'))
assert len(designs) == 2
pins = {}
for path in [r/main,*[r/n for n in tests],*docs,Path(__file__),*designs]:
    name = str(path.relative_to(r))
    assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+name])).hexdigest() == sha(path)
    if path in designs:
        assert hashlib.sha256(subprocess.check_output(['git','show','origin/main:'+name])).hexdigest() == sha(path)
    pins[name] = sha(path)
case_names = {n:re.findall(r'@Test\s+void\s+(\w+)\(', (r/n).read_text()) for n in tests}
assert [len(case_names[n]) for n in tests] == [4,3,3,2,2]
spec = docs[0].read_text()
review_ids = re.findall(r'^\| (WBRO\d{3}) \|', spec, re.M)
assert review_ids == ['WBRO'+str(i).zfill(3) for i in range(1,19)]
normalp = r.parent/'pgpt-runs/PG379/pg20990-outbox-required-six-main-compile-v1/manifest.safe.json'
staticp = r.parent/'pgpt-runs/PG379/pg20992-outbox-required-six-static-reactor-v1/manifest.safe.json'
assert sha(normalp) == '1db34d8f2ccee9fc90244bea86c3e446be0c0e010c66516a1e25c92df3426618'
assert sha(staticp) == '2d3130234ce662ebf2b0bb1f57e74c123ec68e7a307feb10844231bd9822a20a'
normal, static = load(normalp), load(staticp)
assert normal['begin']['inputHashes'][main] == pins[main]
assert static['actualExit'] == 0 and static['source'] == normal['source']
assert static['normalCompileManifestSha256'] == sha(normalp)
assert static['jarsStillEqualCompile'] and static['sourceInputsUnchanged']
cls = 'dev/codex/schubert/nk/web/messaging/WebBrokerContexts'
physical = {k:v for k,v in normal['normalPhysicalClassHashes'].items()
            if k == 'web:'+cls+'.class' or k.startswith('web:'+cls+'$')}
assert len(physical) == 1
out = r/'evidence/01_PT/005_NK-MSG-001/evidence/PG21890-web-broker-whole-static-review-v1'
assert not out.exists()
out.mkdir()
value = dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=head,
    productionCoreMain=normal['source'],main=main,inputHashes=pins,physicalHashes=physical,
    designSource=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip(),
    reviewIds=review_ids,existingTestDesignMethods=case_names,existingTestDesignMethodCount=14,
    staticReferences=[dict(path=str(p),sha256=sha(p)) for p in [normalp,staticp]],
    firstPass='ACQUISITION_ORDER_DATA_LIFETIME',secondPass='STATE_FAILURE_PRIORITY_BORROW_BOUNDARY',
    status='STATIC_DESIGN_REVIEW_ONLY_DYNAMIC_HOLD_SCOPE_UNRESOLVED',
    unresolved=['explicit concurrent open-close measurement','real provider/runtime/native postconditions',
                'current whole dependency execution and four coverage counters','exact refusal scope'],
    productTestsExecuted=0,newProductTests=0,newMethods=0,newSourceProofs=0,newAcceptance=0,
    coverage=None,ptExecutionExempt=False,whole451Accepted=False,formalUpdated=False,effortRate=None)
(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,reviewCriteria=18,existingMethodsReviewedOnly=14,
                     productTestsExecuted=0,manifestSha256=sha(out/'manifest.json'))))
