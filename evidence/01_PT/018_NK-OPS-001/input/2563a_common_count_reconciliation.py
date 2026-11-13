"""Preserve the failed historical-count premise and reconcile current whole-class counts before source repair."""
from pathlib import Path
import json, hashlib, datetime

r = Path.cwd()
b = r / 'evidence/01_PT/018_NK-OPS-001'
i = b / 'input'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def write(path, value):
    assert not path.exists()
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')

e = b / 'evidence/PG30672-common58-worker-and-exact-source-closure-v1'
p = i / '2562_common58_worker_and_source_closure.py'
assert not (e / 'manifest.json').exists()
(e / 'executed-original-producer.py.txt').write_bytes(p.read_bytes())
write(e / 'manifest.json', dict(
    actualExit=1, status='PRE_SOURCE_MUTATION_COUNT_ASSERTION_FAILURE',
    configuredCorrelatedTests=9, actualWholeCorrelatedTests=11,
    productTestsExecuted=0, sourceChanged=False,
    reason='Prior46 had9; current class already has QA054 tests010/011 committed55f4b3265b. Same six whole classes total60; newdefinitions0; estimate retained.'))

spec = r / 'evidence/01_PT/020_NK-CHR-001/025_common原五十八計画から現六十への着手照合訂正.md'
assert not spec.exists()
spec.write_text('''# common whole class実物照合：58計画から60へ訂正

元024・GROUP_START5239・当群見積り.85/2.55/5.1cap6を保存。PG30672は原Correlated9と仮定したassertでsource変更前に失敗、試験/外部起動0。現在classは55f4b3265bで承認済QA054の010/011が既追加され全11。既013仕様/PG29276・29284以後の証跡へ対応し、新発見/新定義2を計上しない。

同じ選択6全classの現在件数はArtifactComparator9/Gate12/GateContract8/GateContractValidatorNegative17/TargetAdapter3/Correlated11=60。Main5全byte/必要wholehelperは旧029c35資格時から不変。変化は既QA054 Test二追加とGateBUG2873/CorrelatedBUG2876 worker是正で、要求/期待JSON/全class選択を減らさない。原46/別source11を新60へ合算せず、当source単一60/全10physicalの真正結果で確認する。

同6全class・worker一caseで見積りは初回cap6内を維持、新費用/原額変更0。着手前件数照合失敗と計画訂正を別記し、旧群名COMMON58は識別子だけ保持、実行ID/expectedInvocationsは60へ明記する。Root/DB/native/Current等HOLD/品質/モデル変更0。新JUnit定義0。
''')
q = b / 'evidence/PG30674-common-whole-count-source-reconciliation-v1'
assert not q.exists()
q.mkdir()
write(q / 'manifest.json', dict(
    actualExit=0, atUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    originalFrozenWholeCount=58, currentWholeCount=60,
    sourceTestAddedPreviously='55f4b3265b', newTestDefinitions=0,
    selectedWholeClassesUnchanged=True,
    estimateUnchanged=dict(low=.85, base=2.55, high=5.1), capPp=6,
    grossBudgetAdded=0,
    correctionSpecification=dict(path=str(spec.relative_to(r)), sha256=sha(spec))))

for name in ['915_障害表.md', '916_横展開管理台帳.md']:
    p = r / 'documents/900_OTHER/910_台帳' / name
    p.write_text(p.read_text() + '\n\n2026-11-14 BUG2876/YKT2387着手前件数訂正: currentCorrelatedは既QA054010/011追加済55f4bで全11、原9はPG29254歴史値。対象worker一caseは同じ、PG30672 source変更前countassert失敗を保存、PG30674/仕様025で同6wholeclass全60へ訂正、新定義/費用/要求/品質変更0。再試験未OPEN。\n')

old = (i / '2562_common58_worker_and_source_closure.py').read_text()
new = old
replacements = {
    'PG30672-common58-worker-and-exact-source-closure-v1': 'PG30676-common60-worker-and-exact-source-closure-v2',
    "before.count('@Test')==9": "before.count('@Test')==11",
    "new.count('@Test')==9": "new.count('@Test')==11",
    "original+':'+str(p.relative_to(r))": "'fcb733e578e5004de9a910fda5e31853b0b97947:'+str(p.relative_to(r))",
    'oldCorrelatedWhole9UnchangedExpectations': 'currentCorrelatedWhole11UnchangedExpectations',
    '[9,12,8,17,3,9]': '[9,12,8,17,3,11]',
    'normal58AndIndependentPostPending': 'normal60AndIndependentPostPending',
    'worker9SourceCorrected': 'worker11SourceCorrected',
}
for before, after in replacements.items():
    assert before in new
    new = new.replace(before, after)
p = i / '2563_common60_worker_and_source_closure.py'
assert not p.exists()
compile(new, str(p), 'exec')
p.write_text(new)
print(json.dumps(dict(actualExit=0, sameSixWholeClasses=60, newDefinitions=0, estimateUnchanged=True)))
