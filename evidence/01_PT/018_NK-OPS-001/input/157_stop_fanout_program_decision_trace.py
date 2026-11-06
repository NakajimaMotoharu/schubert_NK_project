"""Bind additive program/decision documentation to existing source facts, not acceptance."""
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
program = r/'documents/400_PGPT/430_構成・追跡/431_Module・Program一覧.md'
decision = r/'documents/400_PGPT/440_判断/441_実装判断記録.md'
section = program.read_text().split('## 現candidate56720',1)[1].split('以下の既trace',1)[0]
assert len(re.findall(r'^\| NK-',section,re.M)) == 5
headings = [int(m[1]) for line in decision.read_text().splitlines() if line.startswith('#')
            for m in [re.search(r'PG-D-?(\d+)',line)] if m]
assert max(headings) == 1141 and headings.count(1141) == 1
assert '全NOT_RUN/HOLD' in section and '追加費/遡及配賦0' in section
normalp = r.parent/'pgpt-runs/PG379/pg21922-consumer-stop-six-main-compile-v1/manifest.safe.json'
assert sha(normalp) == 'e925b4c24e0eff9e70f7b3fad0b595d80e90f1a444c87329215d6e4b3d5d8d1f'
normal = load(normalp)
descriptorp = r/'evidence/01_PT/018_NK-OPS-001/evidence/PG21942-current56720-static-artifact-lineage-v1/manifest.json'
assert sha(descriptorp) == 'bb8ed9e6d7e33cc2c29e912cb35e055b73f527026b3c49e3b3aab8fcc36d6673'
descriptor = load(descriptorp)
artifactp = descriptorp.parent/'artifacts.json'
assert sha(artifactp) == descriptor['files']['artifacts.json']
artifacts = {x['path']:x for x in load(artifactp)}
root = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/messaging/inbound/'
expected = [
    ('ApiMessagingRuntime',['close','closeGroups'],'WBS-P005-03',[1,2,3,4,5,6]),
    ('SyncRequestConsumers',['stopDelivery','close'],'WBS-P005-03',[1,2,3,4,5,6]),
    ('WebLogConsumers',['stopDelivery','close'],'WBS-P006-05',[1,2,3,4,5,6]),
    ('QuestionWorkConsumers',['stopDelivery','close'],'WBS-P012-01',[1,3,4,5,6]),
    ('InboundConsumerGroup',['stopDelivery','close'],'WBS-P005-03',[1,2,3,4,5,6])]
rows = []
spec = r/'evidence/01_PT/005_NK-MSG-001/026_APIconsumer停止fanout是正・独立PT仕様.md'
spec_rows = [line for line in spec.read_text().splitlines() if line.startswith('| PT-JMS-STOP-GROUP')]
assert len(spec_rows) == 6 and all('NOT_RUN/HOLD' in line for line in spec_rows)
for name,methods,owner,ids in expected:
    n = root+name+'.java'
    assert name in section and owner in section and sha(r/n) == normal['begin']['inputHashes'][n] == artifacts[n]['sha256']
    assert artifacts[n]['owner'] == artifacts[n]['costOwner'] == owner
    assert artifacts[n]['additionalBudgetPp'] == 0
    text = (r/n).read_text()
    for method in methods:
        assert re.search(r'\bvoid\s+'+method+r'\s*\(',text)
    tests = ['PT-JMS-STOP-GROUP'+str(i).zfill(3) for i in ids]
    assert all(t in spec.read_text() for t in tests)
    rows.append(dict(path=n,className=name,methods=methods,canonicalOwner=owner,
        canonicalArtifactCostOwner=owner,commonCorrectionGroupCostOwner='WBS-P005-03',
        additionalBudgetPp=0,retrospectiveCostReallocation=False,mainSha256=sha(r/n),
        pendingTests={t:'NOT_RUN_HOLD' for t in tests},requirementIds=['MQ-003','MQ-006','MQ-008','MQ-010'],
        ui=['212','213','231','251'],ss=['312','321/SSC314','342'],decision='PG-D1141',
        bugsOpen=['BUG-2407','YKT-2152'],codeMetadataOnly=name=='InboundConsumerGroup'))
for path in [program,decision,spec,Path(__file__)]:
    assert hashlib.sha256(subprocess.check_output(['git','show',head+':'+str(path.relative_to(r))])).hexdigest() == sha(path)
out = r/'evidence/01_PT/018_NK-OPS-001/evidence/PG21988-stop-program-decision-method-trace-v1'
assert not out.exists()
out.mkdir()
value = dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=head,
    productionCoreMain=normal['source'],programDoc=dict(path=str(program.relative_to(r)),sha256=sha(program)),
    decisionDoc=dict(path=str(decision.relative_to(r)),sha256=sha(decision)),rows=rows,
    sharedCostCount=1,relatedLeafAdditionalBudgets=0,newBusinessScope=False,
    productTestsExecuted=0,newMethods=0,newSourceProofs=0,newAcceptance=0,coverage=None,
    wholeG13Accepted=False,whole451Accepted=False,formalUpdated=False,effortRate=None)
(out/'manifest.json').write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(actualExit=0,programRows=5,decision='PG-D1141',newAcceptance=0,
                     manifestSha256=sha(out/'manifest.json'))))
