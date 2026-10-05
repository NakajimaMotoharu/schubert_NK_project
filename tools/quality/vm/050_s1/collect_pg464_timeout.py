"""Hash-only operator evidence; no raw private state, credential or permit publication."""
import datetime, hashlib, json, pathlib, subprocess
ROOT = pathlib.Path('/home/mini/codex/project1/work/pgpt-foundation')
WORK = pathlib.Path('/home/mini/codex/project1/work/pgpt-runs/PG379')
OUT = ROOT / 'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG464-timeout-native-v1'
assert not OUT.exists()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
logs = {}
for name, token in {
    'pg464-timeout-isolation-verify-v1.log': 'PG464',
    'pg464-timeout-isolation-v1.log': 'newOwnedScopesReturnedNormally=true',
    'pg464-timeout-retirement-verify-v1.log': 'PG464',
    'pg464-timeout-retirement-v1.log': 'newOwnedScopesReturnedNormally=true',
    'pg464-timeout-peers-v2.log': '18',
    'pg464-timeout-isolation-tests-v2.log': '60',
    'pg464-timeout-retirement-tests-v2.log': '10',
    'pg464-code-tests-v2.log': '72',
}.items():
    p = WORK / name
    assert token in p.read_text()
    logs[name] = {'sha256': sha(p), 'size': p.stat().st_size}
sources = {str(p.relative_to(ROOT)): sha(p) for p in (ROOT/'tools/quality/vm/050_s1').glob('Pg464*.java')}
classes = {str(p.relative_to(WORK)): sha(p) for folder in ['pg464-timeout-tool-v2', 'pg464-code-tools-v2'] for p in (WORK/folder).glob('*.class')}
data = {'id': OUT.name, 'collectedAt': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'headAtCollection': subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    'sourceDirtyAtCollection': True, 'branch': 'dev-foundation',
    'deployedSource': '11c1feb1c0b51543f98c28e3f54213274648f06f',
    'testIds': ['PT-OPS-ISO464001','PT-OPS-RET464001','PT-OPS-CODE464001'],
    'independentToolAssertions': {'peers':18,'isolation':60,'retirement':10,'codeOnly':72},
    'actualCompletedCommands': [
        {'class':'Pg464TimeoutIsolation','mode':'verify','session':76660,'exitCode':0},
        {'class':'Pg464TimeoutIsolation','mode':'isolate','session':42672,'exitCode':0},
        {'class':'Pg464TimeoutRetirement','mode':'verify','session':35169,'exitCode':0},
        {'class':'Pg464TimeoutRetirement','mode':'retire','session':22935,'exitCode':0}],
    'postconditions': {'allNineTerminal':True,'preservedFullFourteenColumnRows':321,
        'originalPendingBackupTransferPreserved':True,'startupNamespaceCount':29,'intentCount':0,
        'canonicalState':'INVALID','newOwnedScopesReturnedNormally':True,'ddlIssued':0,'newStart':0},
    'oldParentExit':143, 'oldParentAccepted':False,'oldUnknownNormalized':False,
    'codeOnlyNativeExecuted':False,'formal':False,'productionPtCredit':0,
    'bugs':['BUG-704','BUG-706','BUG-707'],'ykt':['YKT-506','YKT-507','YKT-504'],'ssc':['SSC-187'],
    'privateLogHashes':logs,'sourceHashes':sources,'classHashes':classes,
    'limits':['Operator assertions are not Production coverage.','New-source full/native pending.',
        'Retirement has no complete.private; normal return uses actual command exits.',
        'Old timeout remains failed; all preservation/private heaps remain outside Git.'],
    'redaction':'Hashes/counts/approved class identity only; private wire/DB/credentials omitted.'}
OUT.mkdir(parents=True,mode=0o750)
(OUT/'manifest.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'manifestSha256':sha(OUT/'manifest.json'),'formal':False}))
