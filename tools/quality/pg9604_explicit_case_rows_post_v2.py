"""Independent prefix-chain parser and all-row rollout check for BUG1752, keeping v1 intact."""
import json
import re
import pg9600_explicit_case_row_post as stage

CORRECTION=stage.ROOT/'evidence/01_PT/018_NK-OPS-001/1947_G13ExplicitCaseRows_初回失敗・是正仕様.md'
CORRECTION_SHA='5f28109745630d7ee953e149cc6b0f87f1c0df22e90476dc292fa22244074df2'

def leading_refs(source):
    lexer=re.compile(r'//[^\r\n]*|/\*[\s\S]*?\*/|"(?:\\.|[^"\\])*"|[A-Za-z_$][A-Za-z0-9_$]*|.',re.S)
    comment=None;found=False
    for match in lexer.finditer(source):
        word=match.group()
        if word=='class':found=True;break
        if word.startswith('/**'):comment=word[3:-2]
    if not found or comment is None:return []
    body=comment.lstrip(' \r\n\t*');at=0;values=[];best=[]
    while at<len(body):
        begin=at
        while at<len(body) and body[at] in '0123456789':at+=1
        if at-begin not in (3,4):break
        values.append(int(body[begin:at]))
        if at<len(body) and body[at] in '/_ :':best=list(values)
        if at>=len(body) or body[at]!='/':break
        at+=1
    return sorted(set(best))

if __name__=='__main__':
    c=stage.data.data;assert c.sha(CORRECTION.read_bytes())==CORRECTION_SHA
    extra=[
      ('/** 1880/1882 WLCLOSE001..004 */ final class T {}',[1880,1882]),
      ('/** 1870/APISTOP001～018 */ class T {}',[1870]),
      ('/** 1870/APISTOP001-018 */ class T {}',[1870]),
      ('/** 2026-10-25 API001 */ class T {}',[]),
      ('/** Arithmetic 1870 values */ class T {}',[]),
      ('/** API001..018 */ class T {}',[]),
      ('/** 1870..1872 */ class T {}',[]),
      ('/**\n * 1870/APISTOP001..018\n */ class T {}',[1870])]
    for text,expected in extra:assert leading_refs(text)==expected
    stage.refs_from_header=leading_refs
    stage.SUBJECT=stage.BASE/'PG9602-explicit-case-row-candidates-v2'
    stage.SUBJECT_SHA='f4fa3e3fe68ef3343c20a7e8cbc8c128918f32cb10bad3b9634a90efe587d3ba'
    stage.OUT=stage.BASE/'PG9604-explicit-case-row-post-v2'
    stage.main()
    primary=json.loads((stage.OUT/'manifest.json').read_bytes())
    delta=json.loads((stage.SUBJECT/'correction-delta.safe.json').read_bytes())
    before_dir=stage.BASE/'PG9598-explicit-case-row-candidates-v1'
    old=c.read_checked(before_dir/'manifest.json','538aedc37867bbc02c373dafde7155c77383c711ec51fb0f17786b123fdd1183')
    new=c.read_checked(stage.SUBJECT/'manifest.json',stage.SUBJECT_SHA)
    before=c.read_checked(before_dir/'method-spec-row-candidates.json',old['candidatesSha256'])
    after=c.read_checked(stage.SUBJECT/'method-spec-row-candidates.json',new['candidatesSha256'])
    assert len(before)==len(after)==5622 and delta['primaryManifestSha256']==stage.SUBJECT_SHA and delta['correctionSpecSha256']==CORRECTION_SHA
    fields={'sourceHeaderDocRefs','referenceStatus','specRowCandidates'}
    differences=[(a,b) for a,b in zip(before,after) if a!=b]
    assert all({k:v for k,v in a.items() if k not in fields}=={k:v for k,v in b.items() if k not in fields} for a,b in zip(before,after))
    assert len(differences)==delta['changedRows']==3618
    assert sum(a['sourceHeaderDocRefs']!=b['sourceHeaderDocRefs'] for a,b in zip(before,after))==delta['changedSourceDocRefs']==3618
    assert sum(a['specRowCandidates']!=b['specRowCandidates'] for a,b in zip(before,after))==delta['changedSelectedSpecRows']==445
    assert all(not row['oracleSemanticsQualified'] and not row['productExecuted'] for row in after)
    result=dict(actualExit=0,source=stage.SOURCE,primaryPostManifestSha256=c.sha((stage.OUT/'manifest.json').read_bytes()),
      producerCorrectionDeltaSha256=c.sha((stage.SUBJECT/'correction-delta.safe.json').read_bytes()),
      correctionSpecSha256=CORRECTION_SHA,additionalLiteralDocRefVectors=len(extra),originalLiteralVectors=primary['literalEdgeVectors'],
      originalFailingVectorUnchanged=True,all5622RowsRecomputed=True,changedRows=3618,changedSelectedSpecRows=445,
      changedFields=sorted(fields),otherFieldsUnchanged=True,allTargetsFixedOrNonApplicable=True,
      fixedTargets=['pg9602.leading_doc_refs','pg9604.leading_refs'],
      nonApplicable=['explicit_case_row_inputs_fixed_corpus_only','pg9554_literal_table_no_numeric_docref'],
      originalFailurePreservedCommit='268850069a86e0d36d1928e7bb1331b1d1242dec',
      bug='BUG-1752',rollout='YKT-1503',productTestsExecuted=0,oracleSemanticsQualified=False,formalUpdated=False)
    c.write(stage.OUT/'correction-post.safe.json',result)
    print(json.dumps(dict(actualExit=0,additionalLiteralDocRefVectors=len(extra),changedRows=3618,changedSelectedSpecRows=445)))
    print('correctionPostSha256='+c.sha((stage.OUT/'correction-post.safe.json').read_bytes()))
