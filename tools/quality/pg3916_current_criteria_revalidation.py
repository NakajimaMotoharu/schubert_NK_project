"""Revalidate existing17/51 against current source/evidence, never award new leaves."""
import hashlib
import inspect
import json
import subprocess
import pg3542_current_criteria_revalidation as previous
from pg3798_hygiene_current_observer import SOURCE

ROOT=previous.ROOT;PMO=previous.PMO;PREVIOUS='4856b3fcaeb4cae983d77757a38dc0bf56a693e2'
PUBLIC=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3916-current-criteria-revalidation-v1'
WITNESS='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3914-current-common-xml-witness-v1/manifest.json'
LATEST=previous.WITNESS
MEASUREMENT='evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG3912-current-wbs-measurement-v1/manifest.json'
EXPECTED=previous.EXPECTED


def foundation_documents(foundation):
    old=previous.read(previous.PUBLIC/'manifest.json')
    prior=old['rows']['WBS-F01']['specificQuality']['changedDocumentReview'];result={}
    for path,digest in foundation['documentSha256'].items():
        current=(ROOT/path).read_bytes()
        if previous.sha(current)==digest:continue
        previous.require(path=='documents/400_PGPT/440_判断/441_実装判断記録.md','unreviewed foundation document change')
        before=previous.git_file(PREVIOUS,path)
        previous.require(previous.sha(before)==prior[path]['newSha256'],'previously reviewed419 policy really matches historical accepted source')
        addition=previous.prepend_only(before,current,'## PG3690/3692')
        result[path]={'priorReviewedSha256':previous.sha(before),'newSha256':previous.sha(current),'additionSha256':addition,'reason':'Only explicit meaning-preserving Checkstyle source-expression decision prepended; all prior policy byte-exact','priorReviewManifestSha256':previous.sha((previous.PUBLIC/'manifest.json').read_bytes())}
    for path,digest in foundation['canonicalDocumentSha256'].items():
        current=previous.git_file('origin/main',path);previous.require(current==(ROOT/path).read_bytes(),'current canonical foundation agreement')
        expected=prior[path]['newSha256']if path in prior else digest
        previous.require(previous.sha(current)==expected,'no unreviewed canonical foundation change since accepted17')
        if path in prior:result[path]={'newSha256':expected,'reason':'Exact previously accepted SSC285 canonical supplement; not a new policy waiver','priorReviewManifestSha256':previous.sha((previous.PUBLIC/'manifest.json').read_bytes())}
    return result


def revalidate():
    raw=inspect.getsource(previous.revalidate)
    for old,new in [('pg3414-outbox-full-qualified-v1','pg3738-hygiene-whole-qualified-v1'),('3712','3714')]:raw=raw.replace(old,new)
    old="    require(len(changed)==1 and changed[0]['owner']=='WBS-P006-02'and changed[0]['path'].endswith('/OutboxJmsSender.java'),'only independently registered unaccepted Outbox change')"
    new="""    require(changed==measurement['artifactChanges'] and len(changed)==260,'all and only actual current941 byte changes independently source-bound')
    accepted_changes=[v for v in changed if v['owner']in EXPECTED]
    require(len(accepted_changes)==19 and all(v['path'].startswith(('src/schubert-nk-protocol/','src/schubert-nk-storage/'))for v in accepted_changes),'exact19 common hygiene scope; no outside accepted contract changes')
    current_hashes={v['path']:v['newSha256']for v in changed}
"""
    if raw.count(old)!=1:raise ValueError('one exact old physical-change boundary')
    raw=raw.replace(old,new)
    for old,new in [("require(sha((ROOT/item['path']).read_bytes())==item['sha256'],'accepted owned artifact byte changed')","require(sha((ROOT/item['path']).read_bytes())==current_hashes.get(item['path'],item['sha256']),'accepted owned artifact must match exact current qualified bytes')"),
                    ("require(sha((ROOT/item['path']).read_bytes())==item['sha256'],'shared class byte changed')","require(sha((ROOT/item['path']).read_bytes())==current_hashes.get(item['path'],item['sha256']),'shared current class must match exact qualified bytes')"),
                    ("'sha256':item['sha256'],'owner'","'sha256':sha((ROOT/item['path']).read_bytes()),'owner'"),
                    ("{x['path']:x['sha256']for x in owned}","{x['path']:sha((ROOT/x['path']).read_bytes())for x in owned}"),
                    ('complete unchanged owned scope and canonical designs','complete unchanged owned scope identities, current qualified common bytes and unchanged canonical contracts')]:
        if old not in raw:raise ValueError('exact current per-artifact review boundary required')
        raw=raw.replace(old,new)
    start=raw.index('    foundation_docs={}')
    end=raw.index("    reviews['WBS-F01']['specificQuality']",start)
    raw=raw[:start]+"    foundation_docs=foundation_documents(foundation)\n"+raw[end:]
    values={**previous.__dict__,'SOURCE':SOURCE,'PREVIOUS':PREVIOUS,'PUBLIC':PUBLIC,'WITNESS':WITNESS,'LATEST':LATEST,'MEASUREMENT':MEASUREMENT,'foundation_documents':foundation_documents}
    exec(compile(raw,'<explicit current17 current bytes oracle quality and dependency bridge>','exec'),values)
    result=values['revalidate']()
    result.update(hygieneAcceptedArtifactCount=19,all941ChangedArtifactCount=260,sourceChangeBasis='Current original3714/545 XML/Test identities, unchanged independent oracle sources and canonical per-task contracts, all owned/shared common-family fourcounter0. No previous-source result substitution.',newLeafCredit=0)
    return result


def main():
    if subprocess.check_output(['git','status','--porcelain']):raise ValueError('clean fixed criterion review')
    result=revalidate();PUBLIC.mkdir();raw=(json.dumps(result,ensure_ascii=False,sort_keys=True)+'\n').encode();(PUBLIC/'manifest.json').write_bytes(raw)
    print(json.dumps({'actualExit':0,'source':SOURCE,'acceptedRevalidated':len(result['rows']),'criteriaRevalidated':result['criteriaRevalidated'],'actualChangedArtifacts':260,'acceptedCommonChangedArtifacts':19,'newLeafCredit':0,'manifestSha256':hashlib.sha256(raw).hexdigest()}));return 0


if __name__=='__main__':raise SystemExit(main())
