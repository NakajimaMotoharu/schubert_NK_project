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
main = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/config/ApiBrokerContexts.java'
root = 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/'
tests = [root+'api/messaging/config/'+n+'.java' for n in [
    'ApiBrokerContextsTest','ApiBrokerFactoryRemainderTest','BrokerGraph334Test',
    'ApiFactoryNativeRetentionTest','ApiFactoryOwnershipTest','ArtemisConnectionFactoryProviderTest']]+[root+'api/file/ApiBrokerContextsCredentialTest.java']
provider = main.replace('ApiBrokerContexts.java','ArtemisConnectionFactoryProvider.java')
docs = [r/'evidence/01_PT/005_NK-MSG-001'/n for n in [
    '023_APIbroker三factory所有静的レビュー仕様.md','024_APIbroker三factory所有静的レビュー結果.md']]
designs = list((r/'documents/300_SS/320_メッセージング').glob('321_*.md'))
designs += list((r/'documents/300_SS/340_batch・基盤').glob('343_*.md'))
assert len(designs) == 2
pins = {}
for path in [r/main,r/provider,*[r/n for n in tests],*docs,Path(__file__),*designs]:
    name = str(path.relative_to(r))
    assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+name])).hexdigest() == sha(path)
    if path in designs:
        assert hashlib.sha256(subprocess.check_output(['git','show','origin/main:'+name])).hexdigest() == sha(path)
    pins[name] = sha(path)
case_names = {n:re.findall(r'@Test\s+void\s+(\w+)\(', (r/n).read_text()) for n in tests}
assert [len(case_names[n]) for n in tests] == [8,3,4,2,4,3,2]
spec = docs[0].read_text()
review_ids = re.findall(r'^\| (ABRO\d{3}) \|', spec, re.M)
assert review_ids == ['ABRO'+str(i).zfill(3) for i in range(1,21)]
normalp = r.parent/'pgpt-runs/PG379/pg20990-outbox-required-six-main-compile-v1/manifest.safe.json'
staticp = r.parent/'pgpt-runs/PG379/pg20992-outbox-required-six-static-reactor-v1/manifest.safe.json'
assert sha(normalp) == '1db34d8f2ccee9fc90244bea86c3e446be0c0e010c66516a1e25c92df3426618'
assert sha(staticp) == '2d3130234ce662ebf2b0bb1f57e74c123ec68e7a307feb10844231bd9822a20a'
normal, static = load(normalp), load(staticp)
assert normal['begin']['inputHashes'][main] == pins[main]
assert normal['begin']['inputHashes'][provider] == pins[provider]
assert static['actualExit'] == 0 and static['source'] == normal['source']
assert static['normalCompileManifestSha256'] == sha(normalp)
assert static['jarsStillEqualCompile'] and static['sourceInputsUnchanged']
cls = 'dev/codex/schubert/nk/api/messaging/config/ApiBrokerContexts'
providercls = cls.replace('ApiBrokerContexts','ArtemisConnectionFactoryProvider')
physical = {k:v for k,v in normal['normalPhysicalClassHashes'].items()
            if k == 'api:'+cls+'.class' or k.startswith('api:'+cls+'$')
            or k == 'api:'+providercls+'.class' or k.startswith('api:'+providercls+'$')}
assert len(physical) == 3
out = r/'evidence/01_PT/005_NK-MSG-001/evidence/PG21900-api-broker-whole-static-review-v1'
assert not out.exists()
out.mkdir()
value = dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=head,
    productionCoreMain=normal['source'],main=main,inputHashes=pins,physicalHashes=physical,
    designSource=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip(),
    reviewIds=review_ids,relatedProvider=provider,primaryCostOwner='WBS-P005-03',relatedCostOwner='WBS-P005-04',relatedAdditionalBudgetPp=0,existingTestDesignMethods=case_names,existingTestDesignMethodCount=26,
    staticReferences=[dict(path=str(p),sha256=sha(p)) for p in [normalp,staticp]],
    firstPass='ACQUISITION_ORDER_DATA_LIFETIME',secondPass='STATE_FAILURE_PRIORITY_BORROW_BOUNDARY',
    status='STATIC_DESIGN_REVIEW_ONLY_DYNAMIC_HOLD_SCOPE_UNRESOLVED',
    unresolved=['explicit concurrent open-close measurement','real provider/runtime/native postconditions including ASYNC credential/broker scope',
                'current whole dependency execution and four coverage counters','exact refusal scope'],
    productTestsExecuted=0,newProductTests=0,newMethods=0,newSourceProofs=0,newAcceptance=0,
    coverage=None,ptExecutionExempt=False,whole451Accepted=False,formalUpdated=False,effortRate=None)
(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,reviewCriteria=20,existingMethodsReviewedOnly=26,
                     productTestsExecuted=0,manifestSha256=sha(out/'manifest.json'))))
