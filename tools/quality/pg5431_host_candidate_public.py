"""Read-only allowlist of actual host candidate; no new signature, guest action or key export."""
import hashlib
import json
import os
from pg5430_ownership_signed_candidate import SOURCE,ROOT,W,NEXT,SIG


def main():
    report=W/'pg5430-candidate-build-v1.safe.json';value=json.loads(report.read_bytes())
    expected={'actualExit':0,'candidateSource':SOURCE,'mainClasses':1664,'tests':3896,'suites':562,
        'artifacts':187,'schema':'028','sql':28,'history':29,'signatureVerified':True,'candidateNotDeployed':True,
        'F03Accepted':False,'formalAccepted':False,'newSourceNativeQualified':False,'deploymentAuthority':False}
    if any(type(value.get(key)) is not type(item) or value[key]!=item for key,item in expected.items()):
        raise ValueError('actual current host-only candidate result')
    raw=(NEXT/'RELEASE-MANIFEST.json').read_bytes();manifest=json.loads(raw)
    if hashlib.sha256(raw).hexdigest()!=value['manifestSha256'] or manifest['source']['commit']!=SOURCE or len(manifest['artifacts'])!=187:
        raise ValueError('actual frozen source and complete signed manifest')
    if SIG.stat().st_size!=64 or hashlib.sha256(SIG.read_bytes()).hexdigest()!=value['signatureSha256']:
        raise ValueError('unchanged genuine64byte signature, never issue another')
    for artifact in manifest['artifacts']:
        path=NEXT/artifact['path']
        if path.is_symlink() or not path.resolve().is_relative_to(NEXT) or path.stat().st_size!=artifact['size'] or hashlib.sha256(path.read_bytes()).hexdigest()!=artifact['sha256']:
            raise ValueError('all actual frozen artifact sizes and bytes')
    output={**value,'hostReportSha256':hashlib.sha256(report.read_bytes()).hexdigest(),
        'stateReference':'HOST_ASSEMBLY_TIME_NOT_CURRENT_GUEST_STATE','vmActions':0,'newSignaturesIssuedByProjection':0,
        'rawKeyOrCredentialExported':False,'acceptedLeafDelta':0,'effortPercent':None}
    out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5430-host-candidate-v1'
    os.umask(0o077);out.mkdir(parents=True)
    path=out/'manifest.json'
    with path.open('x') as stream:json.dump(output,stream,ensure_ascii=False,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    print(json.dumps({'actualExit':0,'release':value['release'],'candidateSource':SOURCE,'BOM':value['manifestSha256'],
        'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'candidateNotDeployedAtAssembly':True,'formalAccepted':False}))


if __name__=='__main__':main()
