"""Metadata-only all1647 findings; fixed nine contract facts, one open style, no suppression."""
import hashlib
import inspect
import json
import os
from lan_server import run
from pg5424_ownership_static import SOURCE,ROOT,W,SLOT

REVIEWS={
 ('api/idempotency/CanonicalField.java','NullAssignment',22):('REQUIRED_CONTRACT','Nullable value preserves absence distinct from empty and clones nonnull bytes; SS324/PT-IDEM001002.','OperationFingerprintTest','value = value == null ? null : value.clone();'),
 ('api/idempotency/CanonicalField.java','ReturnEmptyCollectionRatherThanNull',27):('REQUIRED_CONTRACT','Nullable byte[] absence is part of canonical fingerprint framing, not an empty collection substitute; SS324/PT-IDEM001002.','OperationFingerprintTest','return value == null ? null : value.clone();'),
 ('api/idempotency/ResponseSnapshotCodec.java','HardCodedCryptoKey',57):('FALSE_POSITIVE','currentKey is runtime constructor input; the string currentKey is an error label, not key material; SS324/PT-IDEM007008.','ResponseSnapshotCodecTest','this.currentKey = validateKey(currentKey, "currentKey");'),
 ('api/logging/RequestLogDetails.java','UnusedReturnValue',70):('REQUIRED_CONTRACT','STRICT peek must consume/check EOF and throw on trailing JSON; its return need not be compared to an impossible non-EOF result; SS351/PT-IDEM012.','RequestLogDetailsTest','reader.peek();'),
 ('batch/platform/BrokerJournalEvidence.java','UnusedReturnValue',334):('REQUIRED_CONTRACT','Pinned STRICT parser EOF validation is a required side effect, not an unused read; SS343/PG-D341.','BrokerJournalEvidenceTest','reader.peek();'),
 ('api/maintenance/InspectorAesCredential.java','NullAssignment',53):('REQUIRED_CONTRACT','Decoded buffer ownership transfers to result; clearing temporary reference prevents finally from erasing the returned live key; SS324/PT-DB-INBOX105112.','InspectorAesCredentialTest','decoded = null;'),
 ('bootstrap/ReleaseInventory.java','UnusedReturnValue',143):('REQUIRED_CONTRACT','STRICT EOF check rejects trailing release data before accepting a signed inventory; SS343/SSC308.','ReleaseInventoryTest','reader.peek();'),
 ('bootstrap/SystemManagerObservation.java','NullAssignment',164):('REQUIRED_CONTRACT','Pending owner clears only after confirmed close; retaining after unknown is mandatory, with null an explicit no-owner state; SS343/PG-D428.','SystemManagerObservationTest','if (current != null && current.closed()) pending = null;'),
 ('web/session/SessionAttributeCodec.java','UnusedReturnValue',124):('REQUIRED_CONTRACT','STRICT EOF check is necessary for session attribute grammar; changing to a second oracle or removing it violates trailing-input rejection; SS314.','SessionAttributeCodecTest','reader.peek();'),
 ('web/revocation/RevocationPayloadCodec.java','UnusedNullCheckInEquals',143):('REVIEW_OPEN_STYLE','Explicit previous-key availability guard is safe under paired constructor invariant; redundancy/style disposition remains open, not an accepted exemption.','RevocationPayloadCodecTest','if (previousVersion != null && version.equals(previousVersion))')}


def collect():
    import hashlib
    import json
    import xml.etree.ElementTree as E
    from pathlib import Path
    path=Path('/home/mini/schubert-nk-pgpt/runs/PG5424-ownership-static-v1/pmd.xml')
    root=E.parse(path).getroot();rows=[]
    for file in root:
        if file.tag.rsplit('}',1)[-1]!='file':continue
        name=file.get('name','')
        prefix='/home/mini/schubert-nk-pgpt/runs/PG5424-ownership-static-input-v1/candidate/'
        if not name.startswith(prefix):raise ValueError('only exact current copied Main paths')
        relative=name[len(prefix):]
        if '..' in Path(relative).parts or not relative.startswith('src/') or '/src/main/java/' not in relative:
            raise ValueError('canonical project Main source paths')
        for ordinal,item in enumerate(file,1):
            if item.tag.rsplit('}',1)[-1]!='violation':continue
            values={key:item.get(key) for key in ('rule','ruleset','priority','beginline','endline','begincolumn','endcolumn')}
            rows.append({'sourcePath':relative,'violationOrdinalInFile':ordinal,**values})
    print(json.dumps({'reportSha256':hashlib.sha256(path.read_bytes()).hexdigest(),'findings':rows}))


def project(data,diagnostic,whole_cases):
    if diagnostic['actualExit']!=0 or diagnostic['productionSource']!=SOURCE or diagnostic['result']['pmd']['rawFindings']!=1647:
        raise ValueError('same current real static diagnostic, not inferred zero')
    result=diagnostic['result']
    if data['reportSha256']!=result['pmd']['reportSha256'] or len(data['findings'])!=1647:
        raise ValueError('all current report findings and original report hash')
    counts={};reviewed=set();rows=[]
    for original in data['findings']:
        row=dict(original);path=row['sourcePath']
        if path not in result['allMainSha256'] or not (ROOT/path).resolve().is_relative_to(ROOT/'src'):
            raise ValueError('only whitelisted current production source paths before reading')
        blob=(ROOT/path).read_bytes()
        if hashlib.sha256(blob).hexdigest()!=result['allMainSha256'][path]:raise ValueError('exact current analyzed source bytes')
        source=blob.decode().splitlines();line=int(row['beginline'])
        if not 1<=line<=int(row['endline'])<=len(source):raise ValueError('actual source span')
        row.update(sourceSha256=hashlib.sha256(blob).hexdigest(),status='NOT_REVIEWED',reason=None,wholeCaseRefs=[])
        counts[row['rule']]=counts.get(row['rule'],0)+1
        hits=[key for key in REVIEWS if path.endswith('/dev/codex/schubert/nk/'+key[0]) and key[1]==row['rule'] and key[2]==line]
        if len(hits)>1:raise ValueError('unambiguous explicit row only')
        if hits:
            key=hits[0];status,reason,test,snippet=REVIEWS[key]
            if snippet not in source[line-1] or key in reviewed:raise ValueError('exact reviewed source fact, no blanket rule exemption')
            reviewed.add(key)
            cases=[case for case in whole_cases if case['class'].endswith('.'+test)]
            if not cases or any(case['result']!='PASS_ORIGINAL_XML' for case in cases):raise ValueError('current original whole suite evidence for every reviewed row')
            row.update(status=status,reason=reason,wholeCaseRefs=[{'testId':case['testId'],'xmlSha256':case['xmlSha256']} for case in cases])
        row['findingId']='F03-PMD-'+hashlib.sha256(json.dumps(original,sort_keys=True).encode()).hexdigest()
        rows.append(row)
    if counts!=result['pmd']['ruleCounts'] or reviewed!=set(REVIEWS) or len({row['findingId'] for row in rows})!=1647:
        raise ValueError('all raw rules/rows and exactly ten individually verified reviews')
    return rows


def main():
    diagnostic=json.loads((W/SLOT/'manifest.safe.json').read_bytes())
    private=W/'pg5426-static-findings-projection-v1';os.umask(0o077);private.mkdir(mode=0o700)
    raw=inspect.getsource(collect)+'\ncollect()\n'
    code,output=run("python3 -B - <<'PG5426'\n"+raw+'\nPG5426',timeout=30)
    with(private/'observer.private.log').open('x') as stream:stream.write(output);stream.flush();os.fsync(stream.fileno())
    if code:raise ValueError('current raw report metadata collection failed; no diagnostic replay')
    whole=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5414-current3896-cases/cases.json'
    rows=project(json.loads(output),diagnostic,json.loads(whole.read_bytes()))
    out=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5426-static-findings-v1';out.mkdir(parents=True)
    counts={status:sum(row['status']==status for row in rows) for status in ('REQUIRED_CONTRACT','FALSE_POSITIVE','REVIEW_OPEN_STYLE','NOT_REVIEWED')}
    value={'actualExit':0,'source':SOURCE,'rawFindings':1647,'reviewed':10,'statusCounts':counts,'findings':rows,
        'pmd':diagnostic['result']['pmd'],'checkstyle':diagnostic['result']['checkstyle'],
        'sameCurrentSixJarAbi':True,'sourceFiles':849,'F03Accepted':False,'formalAccepted':False,'acceptedLeafDelta':0,
        'wholeCaseProjectionSha256':hashlib.sha256(whole.read_bytes()).hexdigest(),
        'diagnosticManifestSha256':hashlib.sha256((W/SLOT/'manifest.safe.json').read_bytes()).hexdigest(),
        'codeEdited':False,'rulesSuppressed':0,'vmActions':0,'testReplays':0,'secretOrRawDiagnosticsExported':False}
    path=out/'manifest.json'
    with path.open('x') as stream:json.dump(value,stream,ensure_ascii=False,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    print(json.dumps({'actualExit':0,'statusCounts':counts,'F03Accepted':False,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}))


if __name__=='__main__':main()
