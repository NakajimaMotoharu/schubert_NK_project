"""Passive provenance/partition verification; discovery never means accepted or untested."""
from pathlib import Path
import datetime
import hashlib
import json
import subprocess
R=Path(__file__).resolve().parents[4]
SRC=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22234-unregistered-main-proof-discovery-v1'
OUT=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22238-unregistered-main-proof-independent-post-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_bytes())
HELD={'SnapshotKeyCloseWitness.java','pg9892_snapshot_key_close_witness.py','RootFailedStartRecoveryTest.java','RootFailedStartPairRecoveryTest.java'}
GUARDED={'TemporaryInfrastructureException.java','WebStartupException.java','FingerprintKeyRing.java','ResponseSnapshotCodec.java'}
def dictionaries(value):
    if isinstance(value,dict):
        yield value
        for v in value.values():yield from dictionaries(v)
    elif isinstance(value,list):
        for v in value:yield from dictionaries(v)
def main():
    assert not OUT.exists();m=load(SRC/'manifest.json');assert m['actualExit']==0 and m['productTestsExecuted']==m['newProductTests']==m['newSourceProofs']==m['newAcceptance']==0
    for name,h in m['files'].items():assert sha(SRC/name)==h
    for key in ['producer','lookupTool']:assert sha(R/m[key]['path'])==m[key]['sha256']
    matrix_path=R.parent/'PMO/pgpt-completion-stage-20261102/source-reuse-matrix.json';assert sha(matrix_path)==m['matrixSha256'];original={v['path'] for v in load(matrix_path)['rows'] if v['evidenceStatus']=='NOT_IN_CURRENT_MEASUREMENT_REGISTRY'}
    assert len(original)==282
    rows=load(SRC/'rows.json');paths={v['path'] for v in rows};excluded=set(m['excludedBeforeIO']);char={v['path'] for v in m['nonProductionRowsExcludedBeforeIO']};nonjava={v['path'] for v in m['nonJavaRowsExcludedBeforeIO']}
    assert len(rows)==len(paths)==274 and len(excluded)==4 and len(char)==4 and not nonjava
    assert paths|excluded|char==original and not (paths&excluded or paths&char or excluded&char)
    assert {Path(v).name for v in excluded}==GUARDED and all(v.startswith('program/characterization/') for v in char)
    assert all(v.startswith('src/') and '/src/main/java/' in v and Path(v).suffix=='.java' and Path(v).name not in HELD|GUARDED for v in paths)
    read=load(SRC/'public-read-set.json');read_map={v['path']:v['sha256'] for v in read};assert len(read)==len(read_map)==m['publicManifestsRead']==7938
    tracked=subprocess.check_output(['git','ls-files','-z','--','evidence/01_PT'],cwd=R).decode().split('\0');eligible={n for n in tracked if n.endswith('/manifest.json') and '.private.' not in n and not set(Path(n).parts)&HELD}
    assert eligible==set(read_map)|set(m['unreadBoundedManifests'])
    # Every selected original read remains byte-identical. No private/unknown binary source is opened.
    origins={}
    for name,h in read_map.items():
        assert name.startswith('evidence/01_PT/') and name.endswith('/manifest.json') and not set(Path(name).parts)&HELD
        p=R/name;assert not p.is_symlink() and p.stat().st_size<=2*1024*1024 and sha(p)==h
    positive=0;receipts=0
    for row in rows:
        assert sha(R/row['path'])==row['currentMainSha256'] and not row['qualificationOrPermissionInferred']
        matches=[]
        for c in row['candidates']:
            name=c['path'];assert read_map[name]==c['manifestSha256'] and c['mainPath']==row['path']
            if name not in origins:origins[name]=list(dictionaries(load(R/name)))
            ds=origins[name];assert any(d.get(row['path'])==c['mainSha256'] for d in ds)
            assert any(d==c['fourCounters'] for d in ds)
            assert c['currentMainByteEqual']==(c['mainSha256']==row['currentMainSha256']) and not c['wholeSourceQualificationInferred'] and not c['acceptanceInferred'] and not c['permissionInferred']
            if c['currentMainByteEqual'] and c['originalExit']==0:matches.append(c)
            receipts+=1
        expected='CURRENT_MAIN_MATCH_SUPPORTED_RECEIPT_REVIEW_REQUIRED' if matches else 'UNKNOWN_OR_UNSUPPORTED_NOT_UNIMPLEMENTED'
        assert row['discoveryStatus']==expected
        positive+=bool(matches)
    assert positive==m['supportedCurrentMainMatchRows']==62 and len(rows)-positive==m['unknownOrUnsupportedRows']==212 and not m['unsupportedMetadata']
    OUT.mkdir();result=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),producerManifest=dict(path=str((SRC/'manifest.json').relative_to(R)),sha256=sha(SRC/'manifest.json')),rows=274,currentMainSupportedCandidates=62,unknownOrUnsupported=212,originalGuarded4AndCharacterization4Excluded=True,all7938PublicHashesReread=True,candidateReceipts=receipts,negativeChecks=['GUARDED_MAIN_EXCLUDED_BEFORE_IO','CHARACTERIZATION_SEPARATE_FROM_PRODUCTION','UNSUPPORTED_IS_NOT_UNTESTED','COUNTER_SUBSET_IS_NOT_WHOLE_SOURCE','ZERO_NEW_ACCEPTANCE','PARTITIONS_UNIQUE_AND_COMPLETE'],productTestsExecuted=0,newProductTests=0,newSourceProofs=0,newAcceptance=0,whole451Accepted=False,effortRate=None,verifier=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__))))
    (OUT/'manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(actualExit=0,rows=274,positive=62,unknown=212,manifestSha256=sha(OUT/'manifest.json'))))
if __name__=='__main__':main()
