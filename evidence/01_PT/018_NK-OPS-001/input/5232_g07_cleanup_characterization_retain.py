"""Resolve the one remaining SDK receipt and retain the unchanged private G07 projection index."""
from pathlib import Path
import json
import re
import runpy

HERE=Path(__file__)
R=runpy.run_path(str(HERE.with_name('5230_g07_cleanup_characterization_delta.py')))
OUT,WORK,RETAIN=map(R.get,('OUT','TEMP','RETAIN'))
U=R['U']


def main():
    compact=U['load']('g07_cleanup_chr_compact','5184_g07_jdbc_metrics_retain_compact.py')
    R['configure'](compact.w)
    b=compact.p
    initial=b.load(OUT/'qualified-cached-initial.json')
    assert initial['unqualifiedBinary']==0 and initial['unresolvedCandidates']==1
    assert initial['commits']==17 and initial['trackedBlobVersions']==315 and initial['findingsCount']==126
    pending=b.load(OUT/'remaining-origins.json')
    [hit]=pending
    assert hit['path'].endswith('/PG39810-f03-storage-bootstrap-whole-static-v1/begin.json')
    assert hit['rule']=='generic-api-key' and hit['findingIndex']==43
    [matched]=[meta for meta in b.load(WORK/'projection.json')
               if meta['path']==hit['path'] and meta['blobOid']==hit['blob']]
    projection=WORK/matched['relativeProjection']
    data=projection.read_bytes()
    assert b.sha(data)==matched['decodedSha256']==b.ref(Path(hit['path']))['sha256']
    line=data.splitlines()[hit['line']-1]
    assert b.sha(line)==hit['lineSha256']
    [(path,hex_digest)]=json.loads(b'{'+line.strip().rstrip(b',')+b'}').items()
    assert json.loads(data)['sdkJars'][path]==hex_digest and re.fullmatch('[0-9a-f]{64}',hex_digest)
    jars=Path.cwd().parent/'toolchain/m2/repository'
    candidate=Path(path)
    assert candidate.is_relative_to(jars) and candidate.suffix=='.jar' and candidate.resolve()==candidate
    p0=line.index(hex_digest.encode())
    assert hit['startColumn']-2<=p0 and hit['endColumn']+1>=p0+len(hex_digest)
    assert b.ref(candidate)['sha256']==hex_digest
    sdk=next(OUT.parent.parent.glob('PG39622*/external-origins.json'))
    class_origins=b.load(sdk)['classOrigins']
    names=sorted(k for k,v in class_origins.items() if v['archive']==b.ref(candidate))
    assert names
    row=dict(hit,ground=dict(kind='Pinned public SpotBugs SDK JAR digest',
                              proof=b.ref(sdk),knownClassOrigins=len(names)))
    detail=OUT/'pinned-sdk-origin.json'
    b.write(detail,[row])
    kinds=dict(initial['categories'])
    kinds[row['ground']['kind']]=1
    assert sum(kinds.values())==126
    b.write(OUT/'qualified-final-private-detail.json',dict(initial,confirmedSecrets=0,unresolvedCandidates=0,
        resultQualifiedForRange=True,categories=kinds,origin=b.ref(detail),
        verifier=b.ref(HERE),originalClosureNotReplayed=True))
    compact.DETAILS=('scan-terminal.json','qualified-cached-initial.json','qualified-final-private-detail.json',
                     'classified-findings.json','remaining-origins.json','binary-qualification.json','pinned-sdk-origin.json')
    compact.main()


if __name__=='__main__':
    main()
