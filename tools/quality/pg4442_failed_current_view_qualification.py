"""Independently classify all saved values/raw journal, without replaying VM proof."""
import inspect
import json
from pg4434_current_candidate_admission_read import authenticate_host
from pg4260_stable_admission_image import execute
from pg4420_shared_manager_full import W

SLOT = 'pg4442-failed-current-view-qualified-v1'


def strict_equal(left, right):
    if type(left) is not type(right): return False
    if type(left) is dict:
        return left.keys() == right.keys() and all(strict_equal(left[k], right[k]) for k in left)
    if type(left) is list:
        return len(left) == len(right) and all(strict_equal(a, b) for a, b in zip(left, right, strict=True))
    return left == right


def journal_rows(raw):
    import json
    def pairs(values):
        result = {}
        for key, value in values:
            if key in result: raise ValueError('duplicate field')
            result[key] = value
        return result
    if type(raw) is not bytes: raise ValueError('raw byte journal required')
    rows = [json.loads(line, object_pairs_hook=pairs) for line in raw.splitlines()]
    if not rows or any(type(r) is not dict or type(r.get('__CURSOR')) is not str or not r['__CURSOR'] for r in rows):
        raise ValueError('all cursor events required')
    if len({r['__CURSOR'] for r in rows}) != len(rows): raise ValueError('duplicate cursor')
    return rows


def qualify(proof):
    import hashlib
    import json
    from pathlib import Path
    base = Path('/var/lib/pgpt-s1-preservation/pg4440-failed-full-image-diagnosis-v1')
    def need(value):
        if not value: raise ValueError('full saved current view refused')
    def read(name, digest):
        raw = (base / name).read_bytes(); need(hashlib.sha256(raw).hexdigest() == digest)
        return json.loads(raw)
    result = proof['result']; diagnosis = result['diagnosis']
    need(proof['actualExit'] == result['actualExit'] == 0 and result['newMARDDBTenRefNormalClose'] is True
         and result['parent143StillFailed'] is True and result['oldParentNormal'] is False
         and result['all24OriginalBackupNativeUnitConfigUnchanged'] is True
         and result['nativePhysicalFiles'] == 58 and result['startupPhysicalFiles'] == 37)
    first = read('canonical-first11.private.json', diagnosis['firstFullSha256'])
    second = read('canonical-second11.private.json', diagnosis['secondFullSha256'])
    a = bytes.fromhex(read('journal-first-raw.private.json', diagnosis['firstJournalSha256'])['hex'])
    b = bytes.fromhex(read('journal-second-raw.private.json', diagnosis['secondJournalSha256'])['hex'])
    ar, br = journal_rows(a), journal_rows(b)
    need(strict_equal(first, second) and strict_equal(ar, br) and strict_equal(first['pid1'], ar))
    need(set(first) == {'units','configuration','rows','pid1','startup','originals','backup','extraDurable','unitFilesActual','runtime','native'}
         and len(first['rows']) == 24 and len(first['units']) == 10
         and sum(v['sha256'] is not None for v in first['native'].values()) == 58
         and sum(v['sha256'] is not None for v in first['startup'].values()) == 37)
    before = read('canonical-before10.private.json', result['canonicalBefore10Sha256'])
    need(strict_equal(before, {k:v for k,v in first.items() if k != 'native'}))
    parent = first['units']['schubert-nk-morning-controller.service']
    need(parent['ActiveState'] == parent['SubState'] == 'failed' and parent['Result'] == 'timeout'
         and parent['ExecMainCode'] == '1' and parent['ExecMainStatus'] == '143'
         and parent['InvocationID'] == 'bbcdb69957764d489a9c757b441542fd')
    need(all(v['MainPID'] == v['ControlPID'] == '0' and v['Job'] == '' for v in first['units'].values()))
    done = Path('/var/lib/schubert-nk/maintenance/attempts/8314450e-0dd5-4986-875c-81f73e1b50b2.done').read_bytes()
    digest = hashlib.sha256(done).hexdigest()
    need(digest == '654073a05ac1101060b235c8dc1e058efb94f0884e4eb87613b7f182b199644a')
    fields = done.decode('ascii').splitlines(); need(len(fields) == 6 and fields[0] == 'NKDONE1' and fields[-1] == '10')
    return {'actualExit':0,'dataViewAccepted':True,'canonicalAdmissionAccepted':False,'allElevenValuesIdentical':True,
        'allRawJournalFieldsCursorsAndEventOrderIdentical':True,'rawJsonObjectKeyOrderOnlyDiffers':a != b,
        'source':proof['source'],'BOM':result['BOM'],'boot':'79a3260a-e16d-42bf-942a-b914ed144c28',
        'canonicalFull11Sha256':diagnosis['firstFullSha256'],'canonicalBefore10Sha256':result['canonicalBefore10Sha256'],
        'guestBeforePath':str(base/'canonical-before10.private.json'),'guestFullPath':str(base/'canonical-first11.private.json'),
        'parentFields':parent,'doneEndedAt':fields[4],'doneSha256':digest,'nativeFiles':58,'startupFiles':37,'tables':24,
        'oldParentNormal':False,'normalReceiptIssued':False,'runtimeAuthorityIssued':False,'nativeCandidateCredit':False,
        'newScopesNormal':True,'formalAccepted':False,'vmActions':0}


def payload():
    proof = json.loads((W / 'pg4440-failed-full-image-diagnosis-v1/manifest.safe.json').read_bytes())
    raw = 'import json\n' + '\n'.join(inspect.getsource(f) for f in [strict_equal, journal_rows, qualify])
    raw += '\nprint(json.dumps(qualify(' + repr(proof) + ')))\n'
    return raw


def main():
    authenticate_host()
    return execute(SLOT, payload(), 60)


if __name__ == '__main__':
    raise SystemExit(main())
