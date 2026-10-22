"""Actual comparable host counter delta, never an effort rate or old PASS import."""
import json
import os
import hashlib
from pg5940_private_lock_compile import BASE,sha
from pg6750_original4189_owned_artifacts import read_whole

KINDS=('LINE','METHOD','CLASS','BRANCH')
OLD='01e41088c6562c3b7d103ae0bacc9f693bc1aad4'
DESIGN_CASES=(
 ('PT-OPS-MANAGER-ABI-001','dev.codex.schubert.nk.bootstrap.SystemdBinderAbiTest','abi001AllOwnedSymbolsDispatchIndependentBoundaryVectors'),
 ('PT-OPS-MANAGER-ABI-002','dev.codex.schubert.nk.bootstrap.SystemdBinderAbiTest','abi002MissingAndUnknownSymbolsRemainUnavailableWithoutInvocation'),
 ('PT-OPS-BREQ-READ-001','dev.codex.schubert.nk.batch.file.BackupRequestReadBoundaryTest','breqRead001UnavailableIsNotMissingAndNeverPublishes'),
 ('PT-OPS-BREQ-READ-002','dev.codex.schubert.nk.batch.file.BackupRequestReadBoundaryTest','breqRead002SecondValidRecordMismatchNeverRetires'),
 ('PT-OPS-BREQ-READ-003','dev.codex.schubert.nk.batch.file.BackupRequestReadBoundaryTest','breqRead003FinalDirectoryChangeNeverRetires'))


def design_trace(cases):
    result=[]
    for test_id,cls,method in DESIGN_CASES:
        hashed={hashlib.sha256(s.encode()).hexdigest()for s in (method,method+'()')}
        found=[r for r in cases if r['class']==cls and r['caseNameSha256'] in hashed]
        if len(found)!=1:raise ValueError('one genuine original case per fixed Design Test ID')
        row=found[0]
        result.append(dict(designTestId=test_id,actualWholeTestId=row['testId'],source=row['source'],
          module=row['module'],className=cls,method=method,xmlSha256=row['xmlSha256'],
          caseNameSha256=row['caseNameSha256'],spec='1476' if cls.endswith('SystemdBinderAbiTest')else '1479'))
    return result


def four_closed(counters):
    return all(k in counters and type(counters[k]['missed']) is int and type(counters[k]['covered']) is int
      and counters[k]['missed']==0 and counters[k]['covered']>0 for k in KINDS)


def compare(before,after):
    if set(before)!=set(after):raise ValueError('same actual original XML class-key scope required')
    changed={};closed=[];reopened=[]
    for name in sorted(before):
        b,a=before[name],after[name]
        if b!=a:changed[name]=dict(before=b,after=a)
        if not four_closed(b) and four_closed(a):closed.append(name)
        if four_closed(b) and not four_closed(a):reopened.append(name)
    return dict(changedActualClassCounters=changed,
      newlyMeasuredFour100=closed,noLongerMeasuredFour100=reopened,
      comparableXmlClasses=len(before),beforeExplicitFour100=sum(map(four_closed,before.values())),
      afterExplicitFour100=sum(map(four_closed,after.values())),
      counterMeaning='ACTUAL_XML_CLASS_DOMAIN; branchless/missing/zero not filled as100; not effort or WBS acceptance')


def main():
    qp,q,cases=read_whole();p=BASE/'PG6726-current4184-cases/qualification.json'
    if sha(p)!='f131379f73f9098237fc600052b58d1c1172778c75c3b36e4e96090914662514':raise ValueError('immutable old original4184')
    old=json.loads(p.read_bytes());cp=p.with_name('cases.json')
    if sha(cp)!='971b309633c17805d3684fd504de0a6c860f72d3ef1ae9b24c8c6ddc8015817e':raise ValueError('immutable old semantic identities')
    if not(old['productionSource']==OLD and old['actualExit']==q['actualExit']==0
      and old['allSourceHashes']==q['allSourceHashes'] and old['allPhysicalMainSha256']==q['allPhysicalMainSha256']):
        raise ValueError('all851 source and1667 physical Main must be exactly the same for this comparison')
    key=lambda row:tuple(row[n] for n in ('module','class','caseNameSha256'))
    oldkeys={key(row)for row in json.loads(cp.read_bytes())};newkeys={key(row)for row in cases}
    if len(oldkeys)!=4184 or len(newkeys)!=4189 or not oldkeys<newkeys:raise ValueError('all genuine original case identities, never count arithmetic as PASS')
    value=dict(actualExit=0,beforeSource=OLD,afterSource=q['productionSource'],beforeWholeQualificationSha256=sha(p),
      afterWholeQualificationSha256=sha(qp),sameMainSourceFiles=851,samePhysicalMain=1667,
      actualBeforeCases=4184,actualAfterCases=4189,newActualCaseIdentities=5,
      acceptedLeafDelta=0,effortPercent=None,formalAccepted=False,nativeQualified=False,ptAlternativeCompleted=0,
      testsExecutedByComparison=0,newCaseTestIdTrace=design_trace(cases),**compare(old['allActualClassCounters'],q['allActualClassCounters']))
    out=BASE/'PG6759-owned-counter-delta-v1';os.umask(0o077);out.mkdir();path=out/'manifest.json'
    with path.open('x')as f:json.dump(value,f,sort_keys=True,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps(dict(actualExit=0,manifestSha256=sha(path),newlyMeasuredFour100=value['newlyMeasuredFour100'],reopened=value['noLongerMeasuredFour100'])))


if __name__=='__main__':main()
