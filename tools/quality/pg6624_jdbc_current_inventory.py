"""Qualified current115 JDBC catches; stable original113 plus two explicit factory scopes."""
import json
import os
from collections import Counter,defaultdict
from pg5940_private_lock_compile import ROOT,W,BASE,sha
from pg6542_jdbc_catch_inventory import sites

SOURCE='d25fcb3f487395f83cdfd0df9ff934812f5fd9b3'
FACTORY='src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/maintenance/InspectorDatabaseConnections.java'


def align(path,old,current):
    if path==FACTORY:
        if len(old)!=1 or old[0]['siteId']!='SQLCATCH-049' or len(current)!=3 or [r['catchVariable'] for r in current]!=['failure','secondary','failure']:
            raise ValueError('explicit049 outer and new114/115 admission/cleanup only')
        return [('SQLCATCH-114',None,current[0]),('SQLCATCH-115',None,current[1]),('SQLCATCH-049',old[0],current[2])]
    if len(old)!=len(current):raise ValueError('other changed cardinality requires review')
    return [(before['siteId'],before,now) for before,now in zip(old,current,strict=True)]


def inventory():
    qp=BASE/'PG6622-session-rollback-qualification-v1/manifest.json'
    if sha(qp)!='4e5fd0ed47bceff1014267a8782b6319981b16e34b1a9e398c0b7b9cca107b67':raise ValueError('original current33 qualification first')
    q=json.loads(qp.read_bytes());pp=W/'pg6622-session-rollback-qualification-v1/manifest.safe.json'
    if q['actualExit']!=0 or q['source']!=SOURCE or sha(pp)!=q['privateManifestSha256']:raise ValueError('exact source/original receipt')
    proof=json.loads(pp.read_bytes());hashes={p.relative_to(ROOT).as_posix():sha(p) for p in ROOT.glob('src/*/src/main/java/**/*.java')}
    if len(hashes)!=851 or hashes!=proof['allSourceHashes']:raise ValueError('all851 current Main fixed')
    original=BASE/'PG6542-jdbc-catch-inventory-v1'
    if sha(original/'manifest.json')!='d8aa3acc4f287da8581fdbdf5c2a25ce8ae94b15c468fd02acae35c043ef4435':raise ValueError('immutable original113 identities')
    if sha(original/'sites.json')!=json.loads((original/'manifest.json').read_bytes())['inventorySha256']:raise ValueError('original rows digest')
    groups=defaultdict(list)
    for row in json.loads((original/'sites.json').read_bytes()):groups[row['sourcePath']].append(row)
    rows=[]
    current_paths={path for path in hashes if ('/schubert-nk-api/' in path or '/schubert-nk-web/' in path) and sites((ROOT/path).read_text())}
    if current_paths!=set(groups):raise ValueError('new SQL catch file outside original scope requires review')
    for path,old in sorted(groups.items()):
        for site,before,now in align(path,old,sites((ROOT/path).read_text())):
            rows.append(dict(siteId=site,sourcePath=path,sourceSha256=hashes[path],
                             originalBodySha256=before['bodyTokenSha256'] if before else None,
                             originalIdRetained=before is not None,**now,
                             acceptance='NOT_ACCEPTED_BY_INVENTORY',currentWholeJoined=False))
    if len(rows)!=115 or {r['siteId'] for r in rows}!={'SQLCATCH-'+str(n).zfill(3) for n in range(1,116)}:
        raise ValueError('all115 distinct stable ids without gaps')
    counts=Counter(r['category'] for r in rows)
    if counts!=Counter(GUARDED_REVIEW=58,RETHROW_OR_ATTACH_REVIEW=57):raise ValueError('reviewed source-only presence count,not inferred acceptance')
    return dict(source=SOURCE,qualificationSha256=sha(qp),actualExit=0,sites=115,categoryCounts=dict(counts),
                originalIdsRetained=113,addedIds=['SQLCATCH-114','SQLCATCH-115'],rows=sorted(rows,key=lambda r:r['siteId']),
                acceptedSites=0,testsExecuted=0,nonSqlScopeNotExhaustive=True,formalAccepted=False,
                ptAlternativeCompleted=0,vmActions=0)


def main():
    value=inventory();out=BASE/'PG6624-jdbc-current115-v1';os.umask(0o077);out.mkdir()
    path=out/'manifest.json'
    with path.open('x') as f:f.write(json.dumps(value,ensure_ascii=False,sort_keys=True,indent=2)+'\n')
    print(json.dumps(dict(actualExit=0,source=SOURCE,sites=115,counts=value['categoryCounts'],acceptedSites=0,sha256=sha(path))))


if __name__=='__main__':main()
