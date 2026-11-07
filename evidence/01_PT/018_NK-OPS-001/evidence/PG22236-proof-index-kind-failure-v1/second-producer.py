"""Discovery only: one bounded public evidence read, no invocation or acceptance inference."""
from pathlib import Path
import hashlib
import json
import subprocess
import datetime
from pgpt_program_proof_lookup import candidate,HELD_NAMES
R=Path(__file__).resolve().parents[4]
B=R.parent/'PMO/pgpt-completion-stage-20261102'
OUT=R/'evidence/01_PT/018_NK-OPS-001/evidence/PG22234-unregistered-main-proof-discovery-v1'
GUARDED={'TemporaryInfrastructureException.java','WebStartupException.java','FingerprintKeyRing.java','ResponseSnapshotCodec.java'}
sha=lambda raw:hashlib.sha256(raw).hexdigest()

def main():
    assert not OUT.exists()
    matrix_path=B/'source-reuse-matrix.json';matrix_raw=matrix_path.read_bytes();matrix=json.loads(matrix_raw)
    rows=[];excluded=[];non_java=[]
    for row in matrix['rows']:
        if row['evidenceStatus']!='NOT_IN_CURRENT_MEASUREMENT_REGISTRY':continue
        name=row['path'];p=Path(name)
        if '/src/main/java/' not in name or p.suffix != '.java':
            non_java.append(dict(path=name,reason='NOT_JAVA_MAIN_DISCOVERY_SCOPE'));continue
        if p.name in HELD_NAMES|GUARDED or any(v in HELD_NAMES for v in p.parts):
            excluded.append(name);continue
        assert name.startswith('src/') and '/src/main/java/' in name and p.suffix=='.java' and '..' not in p.parts
        path=R/name;assert path.is_file() and not path.is_symlink()
        rows.append(dict(path=name,currentMainSha256=sha(path.read_bytes()),className=p.stem,candidates=[]))
    names=subprocess.check_output(['git','ls-files','-z','--','evidence/01_PT'],cwd=R).decode().split('\0')
    read=[];unread=[];schema_errors=[]
    for name in names:
        if not name.endswith('/manifest.json') or '.private.' in name or any(v in HELD_NAMES for v in Path(name).parts):continue
        path=R/name
        if path.is_symlink() or not path.is_file() or path.stat().st_size>2*1024*1024:
            unread.append(name);continue
        raw=path.read_bytes();read.append(dict(path=name,sha256=sha(raw)))
        applicable=[row for row in rows if row['className'].encode() in raw]
        if not applicable:continue
        value=json.loads(raw)
        if not isinstance(value,dict):continue
        for row in applicable:
            try:found=candidate(value,row['className'],row['currentMainSha256'])
            except (ValueError,TypeError,KeyError):
                schema_errors.append(dict(path=name,className=row['className'],status='UNSUPPORTED_METADATA_NOT_PRODUCT_FAILURE'));continue
            if found is not None and found['mainPath']==row['path']:
                row['candidates'].append(dict(path=name,manifestSha256=sha(raw),**found))
    for row in rows:
        matches=[v for v in row['candidates'] if v['currentMainByteEqual'] and v['originalExit']==0]
        row['discoveryStatus']='CURRENT_MAIN_MATCH_SUPPORTED_RECEIPT_REVIEW_REQUIRED' if matches else 'UNKNOWN_OR_UNSUPPORTED_NOT_UNIMPLEMENTED'
        row['qualificationOrPermissionInferred']=False
    OUT.mkdir();(OUT/'rows.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n');(OUT/'public-read-set.json').write_text(json.dumps(read,ensure_ascii=False,indent=2)+'\n')
    manifest=dict(actualExit=0,atJST=datetime.datetime.now().astimezone().isoformat(),source=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),productionCoreMain='7aed8eace7c844c2f79f2e39db766faf914890d5',matrixSha256=sha(matrix_raw),matrixRows=282,nonJavaRowsExcludedBeforeIO=non_java,rows=len(rows),excludedBeforeIO=excluded,supportedCurrentMainMatchRows=sum(v['discoveryStatus'].startswith('CURRENT_') for v in rows),unknownOrUnsupportedRows=sum(v['discoveryStatus'].startswith('UNKNOWN_') for v in rows),publicManifestsRead=len(read),unreadBoundedManifests=unread,unsupportedMetadata=schema_errors,productTestsExecuted=0,newProductTests=0,newSourceProofs=0,newAcceptance=0,whole451Accepted=False,effortRate=None,files={n:sha((OUT/n).read_bytes()) for n in ['rows.json','public-read-set.json']},producer=dict(path=str(Path(__file__).relative_to(R)),sha256=sha(Path(__file__).read_bytes())),lookupTool=dict(path='tools/quality/pgpt_program_proof_lookup.py',sha256=sha((R/'tools/quality/pgpt_program_proof_lookup.py').read_bytes())))
    (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:manifest[k] for k in ['actualExit','rows','supportedCurrentMainMatchRows','unknownOrUnsupportedRows','publicManifestsRead','productTestsExecuted']}))
if __name__=='__main__':main()
