"""Emit apply_patch for SSC234 physical scope/owner join, preserving historical qualification."""
import difflib
import hashlib
import json
from pathlib import Path

T = Path(__file__).resolve().parents[4]
B = T / 'documents/400_PGPT/470_PMO'
NEW = 'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/FixedNativeCoverageTerminal.java'
CLASS = 'dev/codex/schubert/nk/bootstrap/FixedNativeCoverageTerminal'
CHANGED = {'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/bootstrap/BootstrapAdminMain.java',
           'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/maintenance/InspectorLauncher.java'} | {
    'src/schubert-nk-bootstrap/src/main/java/dev/codex/schubert/nk/bootstrap/' + n + '.java'
    for n in ('FixedNativeCoverageCheckpoint', 'FixedNativeCoverageProfile', 'NativeCoveragePrivateFile')}


def transform(raw, edit):
    lines = raw.splitlines(keepends=True)
    for i, line in enumerate(lines):
        try:
            value = json.loads(line.strip().rstrip(','))
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict) and edit(value):
            prefix = line[:len(line)-len(line.lstrip())]
            lines[i] = prefix + json.dumps(value, ensure_ascii=False, separators=(',', ':')) + (',' if line.rstrip().endswith(',') else '') + '\n'
    return ''.join(lines)


def main():
    changes = {}
    p = B / '485_WBS網羅性・受入対応.json'; old = p.read_text()
    assert not any(a['path'] == NEW for a in json.loads(old)['artifacts'])
    seen = set()

    def artifact(a):
        if a.get('path') not in CHANGED: return False
        seen.add(a['path']); a['previousCandidateSha256'] = a['sha256']
        a['sha256'] = hashlib.sha256((T / a['path']).read_bytes()).hexdigest()
        a['candidateProvenance'] = {'candidateSource':'e24b246d5d83762650eda5574188d3b4f59fe501',
            'baselineSource':'1ec19782a1afe22d1de75b05f4cd12b8a8a8a172','decision':'SSC234',
            'evidence':'587/PG745 selected88/static2zero','state':'HOST_LIMITED_NOT_DEPLOYED','accepted':False}
        return True

    new = transform(old, artifact); assert seen == CHANGED
    new = new.replace('"javaOuterClasses": 810', '"javaOuterClasses": 811').replace('"artifacts": 935', '"artifacts": 936').replace('"sharedClasses": 36', '"sharedClasses": 37')
    a = {'path':NEW,'kind':'JAVA','module':'bootstrap','class':CLASS,'owner':'WBS-P018-08','costOwner':'WBS-P018-08',
         'basis':'SSC234 finite same-owner measurement lifecycle','sha256':hashlib.sha256((T/NEW).read_bytes()).hexdigest(),
         'acceptance':'UNASSESSED','counterApplicability':'EXECUTABLE_OR_MEASUREMENT_REQUIRED',
         'candidateProvenance':'PG745/core27L18B5M1C100; actual native not accepted'}
    new = new.replace('  "artifacts": [\n', '  "artifacts": [\n    '+json.dumps(a,ensure_ascii=False,separators=(',',':'))+',\n',1)
    a = {'module':'bootstrap','class':CLASS,'owner':'WBS-P018-08','consumers':['WBS-P010-05','WBS-P004-04'],
         'commonImplementationChargedOnce':True,'consumerRule':'共通製造/PT/counter費はP018-08だけ、entry固有順序/receipt/exit oracleは各consumer、二重計上0。'}
    new = new.replace('  "sharedOwnership": [\n','  "sharedOwnership": [\n    '+json.dumps(a,ensure_ascii=False,separators=(',',':'))+',\n',1)
    a = {'id':'SCOPE-V2-003','type':'INTERNAL_MEASUREMENT_CLASS','wbs':'WBS-P018-08','owner':'WBS-P018-08',
         'reason':'SSC234 finite tail; one new Java outer/shared class, existing budget subset, no business scope/accepted task',
         'addedArtifacts':1,'addedJavaOuterClasses':1,'addedSharedClasses':1,'acceptedDelta':0,'budgetDeltaPp':0}
    new = new.replace('  "scopeChanges": [\n','  "scopeChanges": [\n    '+json.dumps(a,ensure_ascii=False,separators=(',',':'))+',\n',1)
    assert len(json.loads(new)['artifacts']) == 936
    changes[p] = old, new
    p = B/'481_PGPT詳細WBS.json'; old = p.read_text(); seen = set()

    def task(a):
        if a.get('id') not in ('WBS-P018-08','WBS-P010-05','WBS-P004-04') or 'ownedArtifacts' not in a: return False
        seen.add(a['id'])
        if a['id']=='WBS-P018-08': a['ownedArtifacts'].append(NEW)
        else: a['sharedClassReferences'].append(CLASS)
        return True

    new = transform(old, task); assert len(seen)==3; json.loads(new); changes[p]=old,new
    p=B/'486_WBS現行実績.json'; old=p.read_text()
    digest=hashlib.sha256(changes[B/'485_WBS網羅性・受入対応.json'][1].encode()).hexdigest()
    previous=json.loads(old)['inventorySha256']; assert old.count(previous)==1
    new=old.replace(previous,digest);changes[p]=old,new
    print('*** Begin Patch')
    for p,(old,new) in changes.items():
        print('*** Update File: '+str(p))
        for line in list(difflib.unified_diff(old.splitlines(),new.splitlines(),n=1))[2:]:
            print('@@' if line.startswith('@@') else line)
    print('*** End Patch')


if __name__=='__main__': main()
