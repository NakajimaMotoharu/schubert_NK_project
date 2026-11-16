"""Reuse only exact source/message/site reviews; leave every unmatched finding unclassified."""
from pathlib import Path
import hashlib
import json

r=Path.cwd();b=r/'evidence/01_PT/018_NK-OPS-001'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
ref=lambda p:dict(path=str(p.relative_to(r)),sha256=sha(p))
load=lambda p:json.loads(p.read_text())
sp=b/'evidence/PG36846-ssc449-boot-batch-static-v1/manifest.json';s=load(sp)
raw=load(sp.parent/'raw-findings.json');assert len(raw)==971 and not s['pmdErrors']
desired={x['path'] for x in raw};by_key={};checked=0
key=lambda x:(x['path'],x['rule'],str(x.get('beginline',x.get('line'))),x['message'])
for config in sorted((b/'input').glob('*.json')):
    c=load(config)
    if not isinstance(c,dict):continue
    if c.get('schema')!='PGPT_CLOSED_HOST_PROFILE_V1' or not desired.intersection(c.get('mainSources',[])):continue
    p=r/c['slots']['preflight']/'manifest.json'
    if not p.is_file():continue
    m=load(p)
    if m.get('actualExit')!=0 or m.get('staticApplicable')!=0 or m.get('unclassified')!=0:continue
    static=m.get('static');admission=m.get('staticAdmission')
    if not static or not admission:continue
    st=r/static['path'];a=r/admission['path']
    if sha(st)!=static['sha256'] or sha(a)!=admission['sha256']:continue
    old=load(st)
    if old.get('fullRootRulesetSha256')!=s['fullRootRuleset']:continue
    checked+=1
    for row in m.get('classified',[]):
        name=row['path']
        if name not in desired or row.get('disposition')!='NOT_APPLICABLE':continue
        if m['inputHashes'].get(name)!=s['inputHashes'][name]:continue
        assert sha(r/name)==s['inputHashes'][name]
        if len(row.get('reason',''))<35:continue
        by_key.setdefault(key(row),dict(priorClassification=row,sourceSha256=s['inputHashes'][name],
            previousQualifiedPreflight=ref(p),previousFullRootStatic=static,
            originalPerSiteAdmission=admission,automaticReacceptance=False))
rows=[];unmatched=[]
for index,row in enumerate(raw):
    prior=by_key.get(key(row));line=(r/row['path']).read_text().splitlines()[int(row['beginline'])-1]
    value=dict(rawFindingIndex=index,raw=row,actualSourceLine=line,
       sourceSha256=s['inputHashes'][row['path']],candidate=prior)
    rows.append(value)
    if prior is None:unmatched.append(value)
out=b/'evidence/PG36851-ssc449-all-profile-pmd971-candidates-v1';assert not out.exists();out.mkdir()
for name,values in [('all-site-candidates.json',rows),('unmatched-sites.json',unmatched)]:
    (out/name).open('x').write(json.dumps(values,ensure_ascii=False,indent=2)+'\n')
(out/'manifest.json').open('x').write(json.dumps(dict(actualExit=0,sourceCore=s['sourceCore'],
    originalStatic=ref(sp),currentFindings=971,candidateMatched=971-len(unmatched),
    unmatched=len(unmatched),originalProfilesChecked=checked,candidatesNotFinalDispositions=True,
    productTestsExecuted=0,newAcceptance=0,formalUpdated=False),indent=2)+'\n')
print(json.dumps(dict(actualExit=0,findings=971,candidates=971-len(unmatched),unmatched=len(unmatched),profiles=checked)))
