"""BUG1752: leading explicit document chain only; immutable original v1 stays preserved."""
import json
import re
import pg9598_explicit_case_row_candidates as stage

CORRECTION=stage.ROOT/'evidence/01_PT/018_NK-OPS-001/1947_G13ExplicitCaseRows_初回失敗・是正仕様.md'
CORRECTION_SHA='5f28109745630d7ee953e149cc6b0f87f1c0df22e90476dc292fa22244074df2'

def leading_doc_refs(text):
    declaration=stage.CLASS.search(text)
    if declaration is None:return []
    comments=re.findall(r'/\*\*([\s\S]*?)\*/',text[:declaration.start()])
    if not comments:return []
    body=re.sub(r'(?m)^[ \t]*\* ?', '',comments[-1]).lstrip()
    match=re.match(r'([0-9]{3,4}(?:/[0-9]{3,4})*)(?=[/_ :])',body)
    return sorted({int(part) for part in match.group(1).split('/')}) if match else []

if __name__=='__main__':
    c=stage.data.data;assert c.sha(CORRECTION.read_bytes())==CORRECTION_SHA
    stage.header_doc_refs=leading_doc_refs
    stage.OUT=stage.BASE/'PG9602-explicit-case-row-candidates-v2'
    stage.main()
    old_dir=stage.BASE/'PG9598-explicit-case-row-candidates-v1'
    old=c.read_checked(old_dir/'manifest.json','538aedc37867bbc02c373dafde7155c77383c711ec51fb0f17786b123fdd1183')
    new=json.loads((stage.OUT/'manifest.json').read_bytes())
    before=c.read_checked(old_dir/'method-spec-row-candidates.json',old['candidatesSha256'])
    after=c.read_checked(stage.OUT/'method-spec-row-candidates.json',new['candidatesSha256'])
    assert len(before)==len(after)==5622 and old['corpusSha256']==new['corpusSha256'] and old['specRowsSha256']==new['specRowsSha256']
    allowed={'sourceHeaderDocRefs','referenceStatus','specRowCandidates'}
    changed=refs=selected=0
    for a,b in zip(before,after):
        assert {k:v for k,v in a.items() if k not in allowed}=={k:v for k,v in b.items() if k not in allowed}
        changed+=a!=b;refs+=a['sourceHeaderDocRefs']!=b['sourceHeaderDocRefs'];selected+=a['specRowCandidates']!=b['specRowCandidates']
    c.write(stage.OUT/'correction-delta.safe.json',dict(actualExit=0,source=stage.SOURCE,
      correctionSpecSha256=CORRECTION_SHA,primaryManifestSha256=c.sha((stage.OUT/'manifest.json').read_bytes()),
      originalManifestSha256='538aedc37867bbc02c373dafde7155c77383c711ec51fb0f17786b123fdd1183',
      originalProducerSourcePreservedCommit='268850069a86e0d36d1928e7bb1331b1d1242dec',
      methodRows=5622,changedRows=changed,changedSourceDocRefs=refs,changedSelectedSpecRows=selected,
      allowedChangedFields=sorted(allowed),allOtherFieldsPreserved=True,oracleOrPtQualificationAdded=False,
      bug='BUG-1752',rollout='YKT-1503',productTestsExecuted=0,formalUpdated=False))
    print(json.dumps(dict(changedRows=changed,changedSourceDocRefs=refs,changedSelectedSpecRows=selected)))
