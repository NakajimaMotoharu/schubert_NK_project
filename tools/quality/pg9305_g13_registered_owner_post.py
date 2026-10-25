"""Independent Git-tree/blob and explicit registry oracle; no resolver or audit helper reused."""
from collections import Counter
import copy
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
from host_tool_invocation import capture, verify

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'evidence/01_PT/018_NK-OPS-001/evidence/provisional'
OUT=BASE/'PG9305-g13-registered-owner-post-v1'
SOURCE='64446a9f8901084a4ad7eba1f66ae975eb2bbdea'
SUBJECT=BASE/'PG9304-g13-registered-owner-gap-v1/manifest.json'
SUBJECT_SHA='bf0371f1eb4a85462ee8db6b265814fe933038b9084243aba933ada81ba162f0'
ENV={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','GIT_NO_LAZY_FETCH':'1','GIT_TERMINAL_PROMPT':'0'}

def digest(raw):return hashlib.sha256(raw).hexdigest()

def assess(value,expected):
    assert value['source']==SOURCE and value['actualExit']==0
    assert value['sourceRows']==expected and len(expected)==len({row['path'] for row in expected})
    assert value['javaPathCount']==len(expected)
    assert value['registryCounts']==dict(Counter(row['registryStatus'] for row in expected))
    modules={}
    for row in expected:
        group=modules.setdefault(row['module']+':'+row['sourceSet'],dict(total=0,registered=0,unregistered=0))
        group['total']+=1; group['unregistered' if row['canonicalOwner'] is None else 'registered']+=1
    assert value['byModuleAndSourceSet']==modules
    for key in ('methodAndRequirementTraceComplete','wholeG13Accepted','whole451Accepted','formalUpdated','costReallocated'):
        assert value[key] is False
    assert value['productTestsExecuted']==value['newTestIds']==value['newMain']==value['newAccepted']==0
    assert value['coverage'] is value['effortPercent'] is value['actualAllocatedPp'] is None

def main():
    invocation=capture(Path(__file__)); assert not OUT.exists() and digest(SUBJECT.read_bytes())==SUBJECT_SHA
    value=json.loads(SUBJECT.read_bytes())
    inventory=json.loads((ROOT/'documents/400_PGPT/470_PMO/485_WBS網羅性・受入対応.json').read_bytes())
    serialize=lambda v:json.dumps(v,sort_keys=True,ensure_ascii=False,separators=(',',':')).encode()
    assert digest(serialize(inventory['artifacts']))==value['original941DatasetSha256']=='ac5dee93b15167133a713c60d255b490400cbaee12362d7f1d0328161318ef99'
    assert digest(serialize(inventory['currentPhysicalCandidate']))==value['historical943DatasetSha256']=='38247ee2b8850d5ab64f37f8d5536c8b14d7aa1962fab7be9c7ec190a930a01a'
    logical={row['path']:row for row in inventory['artifacts']}; assert len(logical)==len(inventory['artifacts'])==941
    prior_path=BASE/'PG9288-api-pure-readiness-trace-v1/manifest.json'
    assert digest(prior_path.read_bytes())==value['prior256ManifestSha256']=='6a721ba74684d07681c61ba56593796363063f6e6eaa313cf62749dc94a2f7a6'
    prior=json.loads(prior_path.read_bytes()); assert prior['source']==SOURCE
    registered={row['path']:row for row in prior['sourceRows']}; assert len(registered)==len(prior['sourceRows'])==256
    tree=subprocess.check_output(['git','ls-tree','-r','-z',SOURCE,'--','src'],cwd=ROOT,env=ENV)
    entries=[]
    for entry in tree.split(b'\0'):
        if not entry:continue
        header,raw_path=entry.split(b'\t',1); path=raw_path.decode('utf-8'); parts=path.split('/')
        if (len(parts)<7 or parts[0]!='src' or parts[1] not in {'schubert-nk-'+name for name in ('protocol','storage','bootstrap','api','web','batch')}
            or parts[2]!='src' or parts[3] not in ('main','test') or parts[4]!='java' or not path.endswith('.java')):continue
        mode,kind,oid=header.decode('ascii').split(); assert mode=='100644' and kind=='blob'
        entries.append((path,oid,parts[1].removeprefix('schubert-nk-'),parts[3]))
    entries.sort()
    batch=subprocess.check_output(['git','cat-file','--batch'],input=''.join(row[1]+'\n' for row in entries).encode(),cwd=ROOT,env=ENV)
    position=0; expected=[]
    for path,oid,module,source_set in entries:
        newline=batch.index(b'\n',position); got,kind,size=batch[position:newline].decode('ascii').split()
        assert got==oid and kind=='blob'; size=int(size)
        data=batch[newline+1:newline+1+size]; position=newline+2+size
        assert len(data)==size and batch[position-1:position]==b'\n'
        file_sha=digest(data); assert digest((ROOT/path).read_bytes())==file_sha
        if path in logical:
            owner,cost=logical[path]['owner'],logical[path]['costOwner']; status='BASELINE_LOGICAL_REFERENCE'
        elif path in registered:
            row=registered[path]; assert row['sha256']==file_sha
            owner,cost=row['canonicalOwner'],row['canonicalCostOwner']; status='CURRENT_EXPLICIT_REVIEWED_CANDIDATE_NOT_ACCEPTED'
        else:owner=cost=None; status='UNKNOWN_NO_EXPLICIT_REGISTRY_ROW'
        expected.append(dict(path=path,sha256=file_sha,module=module,sourceSet=source_set,
          registryStatus=status,canonicalOwner=owner,canonicalCostOwner=cost))
    assert position==len(batch)
    assess(value,expected)
    unknown=next(i for i,row in enumerate(expected) if row['canonicalOwner'] is None)
    known=next(i for i,row in enumerate(expected) if row['canonicalOwner'] is not None)
    rejected=[]
    for name,mutate in (
      ('missing-denominator-row',lambda v:v['sourceRows'].pop()),
      ('duplicate-denominator-row',lambda v:v['sourceRows'].append(copy.deepcopy(v['sourceRows'][0]))),
      ('unknown-guessed-owner',lambda v:v['sourceRows'][unknown].update(canonicalOwner='WBS-G13.07')),
      ('single-cost-field-forged',lambda v:v['sourceRows'][known].update(canonicalCostOwner='WBS-G13.07')),
      ('wrong-source',lambda v:v.update(source='0'*40)),
      ('formal-acceptance-invented',lambda v:v.update(formalUpdated=True)),
      ('unknown-count-zeroed',lambda v:v['registryCounts'].update(UNKNOWN_NO_EXPLICIT_REGISTRY_ROW=0)),
      ('inferred-effort',lambda v:v.update(effortPercent=60))):
        changed=copy.deepcopy(value); mutate(changed)
        try:assess(changed,expected)
        except (AssertionError,KeyError,TypeError):rejected.append(name)
        else:raise AssertionError('forged registry measurement accepted')
    verify(invocation); OUT.mkdir()
    with (OUT/'manifest.json').open('x') as stream:
        json.dump(dict(actualExit=0,source=SOURCE,timeUTC=dt.datetime.now(dt.timezone.utc).isoformat(),invocation=invocation,
          auditManifestSha256=SUBJECT_SHA,independentGitTreeJavaPaths=len(expected),allGitBlobAndCurrentFileHashesMatch=True,
          registryCounts=value['registryCounts'],byModuleAndSourceSet=value['byModuleAndSourceSet'],
          metadataCounterexamples=rejected,original941AndHistorical943Preserved=True,
          auditHelperImported=False,ownerResolverImported=False,productTestsExecuted=0,coverage=None,
          wholeG13Accepted=False,whole451Accepted=False,formalUpdated=False,newAccepted=0,effortPercent=None),stream,sort_keys=True,indent=2)
        stream.write('\n')
    print(json.dumps(dict(actualExit=0,javaPaths=len(expected),metadataCounterexamples=len(rejected),manifestSha256=digest((OUT/'manifest.json').read_bytes()))))

if __name__=='__main__':main()
