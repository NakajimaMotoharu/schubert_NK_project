"""Current source-only JDBC boundary map; lexical presence is not test/receiver acceptance."""
import json
import os
from collections import Counter, defaultdict
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6542_jdbc_catch_inventory import LEX, balanced, sites

SOURCE='e033db0f806549a20adb01e788f5d1d5e2d73d92'


def bodies(text):
    tokens=[(('LITERAL' if m.group().startswith(('"',"'")) else m.group()),m.start())
            for m in LEX.finditer(text) if not m.group().startswith(('//','/*'))]
    result=[]
    for at,(value,offset) in enumerate(tokens):
        if value!='catch':continue
        parameter_end=balanced(tokens,at+1,'(',')')
        header=[x for x,_ in tokens[at+2:parameter_end]]
        end=balanced(tokens,parameter_end+1,'{','}')
        body=[x for x,_ in tokens[parameter_end+2:end]]
        result.append(dict(line=text.count('\n',0,offset)+1,header=header,body=body))
    return result


def align(old,current):
    if len(old)!=len(current):raise ValueError('changed SQL catch cardinality requires explicit remap')
    return list(zip(old,current,strict=True))


def main():
    qp=BASE/'PG6568-readiness-qualification-v1/manifest.json'
    if sha(qp)!='f0d030122e89465916d435906aeb0d7796ec1ba721ccaa79e0fc226605945431':
        raise ValueError('exact qualified current graph source first')
    q=json.loads(qp.read_bytes());pp=W/'pg6568-readiness-qualification-v1/manifest.safe.json'
    if q['source']!=SOURCE or q['actualExit']!=0 or sha(pp)!=q['privateManifestSha256']:
        raise ValueError('genuine original receipt')
    private=json.loads(pp.read_bytes())
    hashes={p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')}
    if len(hashes)!=851 or hashes!=private['allSourceHashes']:
        raise ValueError('all851 Main bytes fixed before current map')
    original=BASE/'PG6542-jdbc-catch-inventory-v1'
    if sha(original/'manifest.json')!='d8aa3acc4f287da8581fdbdf5c2a25ce8ae94b15c468fd02acae35c043ef4435':
        raise ValueError('immutable original113 identity first')
    om=json.loads((original/'manifest.json').read_bytes())
    if sha(original/'sites.json')!=om['inventorySha256']:raise ValueError('original113 rows hash')
    groups=defaultdict(list)
    for row in json.loads((original/'sites.json').read_bytes()):groups[row['sourcePath']].append(row)
    rows=[];markers=[]
    for path,old in sorted(groups.items()):
        text=(ROOT/path).read_text();current=sites(text)
        for before,now in align(old,current):
            body=next(b['body'] for b in bodies(text) if b['line']==now['beginLine'])
            rows.append(dict(siteId=before['siteId'],sourcePath=path,currentSourceSha256=hashes[path],
                originalBodySha256=before['bodyTokenSha256'],**now,
                returnsFalse=['return','false',';'] in [body[i:i+3] for i in range(len(body)-2)],
                factoryCatalog=['throw','unavailable','(',')',';'] in [body[i:i+5] for i in range(len(body)-4)],
                acceptance='NOT_ACCEPTED_BY_SOURCE_SEARCH',currentMethodPtJoined=False))
        for row in bodies(text):
            if 'SQLException' in row['header']:continue
            body=row['body']; variable=row['header'][-1]
            if 'new' in body or 'getSuppressed' in body or 'getSQLState' in body:
                markers.append(dict(sourcePath=path,sourceSha256=hashes[path],line=row['line'],
                    types=row['header'],guardPresent=any(body[i:i+4]==['preserveFatal','(',variable,')'] for i in range(len(body)-3)),
                    applicability='PENDING_RESOURCE_OR_PURE_INPUT_EXCEPTION_REVIEW'))
    counts=Counter(r['category'] for r in rows)
    if len(rows)!=113 or counts!=Counter(GUARDED_REVIEW=30,TRANSLATION_REVIEW=19,
            SQLSTATE_REVIEW=3,RETHROW_OR_ATTACH_REVIEW=61):
        raise ValueError('exact current113 lexical counts, not fabricated coverage')
    out=BASE/'PG6576-jdbc-current-boundary-map-v1';os.umask(0o077);out.mkdir()
    for name,value in (('sites.json',rows),('non-sql-markers.json',markers)):
        with (out/name).open('x') as f:
            json.dump(value,f,ensure_ascii=False,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    value=dict(actualExit=0,source=SOURCE,inputQualificationSha256=sha(qp),sites=113,
        categoryCounts=dict(counts),falseOrFactorySites=[r['siteId'] for r in rows if r['returnsFalse'] or r['factoryCatalog']],
        nonSqlMarkerCandidates=len(markers),sitesSha256=sha(out/'sites.json'),markersSha256=sha(out/'non-sql-markers.json'),
        acceptedSites=0,testsExecuted=0,formalAccepted=False,ptAlternativeCompleted=0,vmActions=0)
    with (out/'manifest.json').open('x') as f:
        json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,sites=113,counts=dict(counts),falseOrFactorySites=value['falseOrFactorySites'],
                         nonSqlMarkerCandidates=len(markers),acceptedSites=0,manifestSha256=sha(out/'manifest.json'))))


if __name__=='__main__':main()
