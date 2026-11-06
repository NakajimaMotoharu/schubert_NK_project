"""Public reference index for avoiding confirmation-only replay; never a qualification gate."""
from pathlib import Path
import hashlib,json,re,sys,unittest

SHA=re.compile(r'[0-9a-f]{64}\Z')
PREFIX='evidence/01_PT/'
def refs(value):
    found=[]
    if isinstance(value,dict):
        p=value.get('path');h=value.get('sha256')
        if isinstance(p,str) and isinstance(h,str) and p.startswith(PREFIX) and '/evidence/' in p and p.endswith('/manifest.json') and '..' not in p.split('/') and SHA.fullmatch(h):found.append((p,h))
        for v in value.values():found.extend(refs(v))
    elif isinstance(value,list):
        for v in value:found.extend(refs(v))
    return found

def pins(manifest):
    # Restrict to the explicit strict-port schema. Other schemas stay unknown.
    if manifest.get('actualExit')!=0 or type(manifest.get('actualExit')) is not int:return {}
    if any(type(manifest.get(k)) is not int or manifest[k]!=0 for k in ['failures','errors','skipped','aborted']):return {}
    if type(manifest.get('tests')) is not int or manifest['tests']<=0:return {}
    if manifest.get('oldExecUnion') is not False or manifest.get('manualCoverageExclusions')!=[]:return {}
    inputs=manifest.get('inputHashes');whole=manifest.get('wholeSourceFourCounter100')
    if not isinstance(inputs,dict) or not isinstance(whole,list):return {}
    return {p:h for p,h in inputs.items() if isinstance(p,str) and p.startswith('src/') and '/src/main/java/' in p and isinstance(h,str) and SHA.fullmatch(h) and p.rsplit('/',1)[-1] in whole}

def compare(saved,current):
    if not saved:return 'NO_STRICT_SAVED_SOURCE_PIN_REVIEW_REQUIRED'
    return 'SAVED_TARGET_BYTES_MATCH_NOT_FULL_QUALIFICATION' if current in saved else 'OBSERVED_TARGET_DRIFT_REVIEW_REQUIRED'

class Contracts(unittest.TestCase):
    def test_reference_is_public_bounded_and_hash_pinned(self):
        p='evidence/01_PT/015_NK-WEB-001/evidence/run/manifest.json';self.assertEqual([(p,'a'*64)],refs({'nested':[{'path':p,'sha256':'a'*64}]}));self.assertEqual([],refs({'path':'/private/raw/manifest.json','sha256':'a'*64}));self.assertEqual([],refs({'path':p,'sha256':'wrong'}));self.assertEqual([],refs({'path':p.replace('/run/','/../'),'sha256':'a'*64}))
    def test_partial_and_red_do_not_become_known_success(self):
        for k,v in [('failures',1),('actualExit',1),('errors',1),('skipped',1),('aborted',1),('oldExecUnion',True)]:
            m=fixture();m[k]=v;self.assertEqual({},pins(m))
    def test_only_whole_source_not_dependency_or_test_is_indexed(self):
        m=fixture();self.assertEqual({TARGET:'a'*64},pins(m));m['wholeSourceFourCounter100']=[];self.assertEqual({},pins(m))
    def test_missing_and_invalid_inputs_remain_unknown(self):
        for k in ['tests','inputHashes','aborted','manualCoverageExclusions']:
            m=fixture();del m[k];self.assertEqual({},pins(m))
    def test_matching_bytes_is_not_a_source_or_gate_transfer(self):
        self.assertEqual('NO_STRICT_SAVED_SOURCE_PIN_REVIEW_REQUIRED',compare([], 'a'*64));self.assertEqual('OBSERVED_TARGET_DRIFT_REVIEW_REQUIRED',compare(['b'*64],'a'*64));self.assertEqual('SAVED_TARGET_BYTES_MATCH_NOT_FULL_QUALIFICATION',compare(['a'*64],'a'*64))
    def test_real_saved_screen_proof_has_preexisting_whole_pin(self):
        p=Path('evidence/01_PT/015_NK-WEB-001/evidence/PG19348-web-saved-screen-eight-v1/manifest.json');self.assertEqual('1d4213dc4dd02d0d68882f4fa74fe3af2374a995f5cab891d936a1135d82d2d8',hashlib.sha256(p.read_bytes()).hexdigest());self.assertEqual({TARGET:'4d3535445d3d460ddabd71c496eaf461ddb6553c9d2e26486374367480ef639f'},pins(json.loads(p.read_text())))
TARGET='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/security/SavedScreenTarget.java'
def fixture():
    return dict(actualExit=0,failures=0,errors=0,skipped=0,aborted=0,tests=8,oldExecUnion=False,manualCoverageExclusions=[],inputHashes={TARGET:'a'*64,'src/x/src/test/java/Test.java':'b'*64,'src/x/src/main/java/Dependency.java':'c'*64},wholeSourceFourCounter100=['SavedScreenTarget.java'])

def build():
    root=Path.cwd();docs=root/'documents/400_PGPT/470_PMO/500_SV計画整備_20261104';found={};docpins={};rejected=[]
    for p in sorted(docs.glob('*.json')):
        if not re.match(r'[5-9][0-9]{2}_',p.name) or int(p.name[:3])>977:continue
        raw=p.read_bytes();docpins[str(p.relative_to(root))]=hashlib.sha256(raw).hexdigest()
        for name,h in refs(json.loads(raw)):found.setdefault(name,set()).add(h)
    known={};records=[]
    for name,hashes in sorted(found.items()):
        if len(hashes)!=1:rejected.append(dict(path=name,reason='MULTIPLE_PINNED_IDENTITIES_REVIEW_REQUIRED'));continue
        p=root/name
        if not p.is_file() or p.is_symlink() or p.stat().st_size>262144:rejected.append(dict(path=name,reason='ABSENT_SYMLINK_OR_SIZE_REVIEW_REQUIRED'));continue
        raw=p.read_bytes();h=hashlib.sha256(raw).hexdigest()
        if h not in hashes:rejected.append(dict(path=name,reason='SAVED_REFERENCE_HASH_MISMATCH'));continue
        m=json.loads(raw);mpins=pins(m)
        if mpins:
            records.append(dict(path=name,sha256=h,source=m['source'],tests=m['tests'],mainPins=mpins))
            for target,pin in mpins.items():known.setdefault(target,[]).append(dict(manifest=name,sha256=h,source=m['source'],targetSha256=pin))
    seed=json.loads((docs/'503_Source証拠再利用判定.json').read_text());rows=[]
    for x in seed['rows']:
        target=x['path'];entries=known.get(target,[]);current=hashlib.sha256((root/target).read_bytes()).hexdigest() if entries else None
        rows.append(dict(path=target,originalSeedStatus=x['evidenceStatus'],knownProofs=entries,status=compare([e['targetSha256'] for e in entries],current),currentTargetSha256=current,sourceQualificationTransferred=False))
    return dict(metadataOnly=True,newProductTests=0,newSourceProofs=0,newAcceptance=0,documentHashes=docpins,checkedReferences=len(found),strictManifestRecords=records,rejectedOrUnsupportedReferences=rejected,rows=rows,note='Incomplete strict-schema index, not all historical evidence. Target byte match is only a reason to examine/reuse prior evidence before execution, never full dependency/source/postcondition qualification; absent proof is UNKNOWN, not permission or zero work.')

if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contracts));assert result.testsRun==6 and result.wasSuccessful();out=Path(sys.argv[1]);assert not out.exists();out.mkdir(parents=True);index=build();index['metadataChecks']=6;(out/'index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(metadataChecks=6,checkedRefs=index['checkedReferences'],strictManifests=len(index['strictManifestRecords']),knownTargets=sum(bool(x['knownProofs']) for x in index['rows']),Product=0)))
