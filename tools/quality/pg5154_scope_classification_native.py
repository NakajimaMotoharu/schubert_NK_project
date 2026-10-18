"""Original237 partition plus explicit new prebuilt-release site; independently join exact source classes."""
import json
import os
import subprocess
import pg5146_scope_classification as inventory
import pg5148_native_fd_selected as selected

SOURCE='86ea5a200bf6cbe5a8d9e79c5cc962ec029a7307'
QUALIFIED='018_NK-OPS-001/evidence/provisional/pg5148-native-fd-green-v2-metadata-v2/manifest.json'


def main():
    root=selected.ROOT
    original=root/('evidence/01_PT/'+inventory.INVENTORY)
    if selected.sha(original)!='9f9c80a5968d5f9a6010e98fa74854c17777c99076eb98d11e3f4e4129870344':
        raise ValueError('immutable original237 inventory')
    qualified=root/('evidence/01_PT/'+QUALIFIED);proof=json.loads(qualified.read_bytes())
    before=json.loads((root.parent/'pgpt-runs/PG379/pg5140-storage-callers-green-v3/manifest.safe.json').read_bytes())['mainDelta']['physicalSha256']
    after=proof['mainDelta']['physicalSha256']
    prefix='storage:dev/codex/schubert/nk/storage/'
    changed={prefix+n+'.class' for n in ('LinuxFileLock','LinuxSealedProof','LinuxStartupAdmission',
           'LinuxFileLock$OwnedDescriptor','LinuxStartupAdmission$Attributes','LinuxStartupAdmission$FdOwner','LinuxStartupAdmission$NativeIo')}
    added={prefix+n+'.class' for n in ('LinuxSealedProof$Descriptor','LinuxStartupAdmission$FdOwners')}
    if (proof['productionCandidateSource']!=SOURCE or proof['actualExit']!=0 or len(after)!=764
        or set(after)-set(before)!=added or set(before)-set(after)
        or {key for key in before if before[key]!=after[key]}!=changed):
        raise ValueError('exact new7 physical changes plus2 additions; all755 others same byte')
    value=json.loads(original.read_bytes())
    counts=inventory.classify(value['files'],
       lambda path:subprocess.check_output(['git','show',SOURCE+':'+path],cwd=root),native=True,evidence_ref=QUALIFIED)
    if counts!={'FIXED_LIMITED':29,'NON_APPLICABLE_BORROWED':1,'UNKNOWN':207}:
        raise ValueError('complete original237 partition without fabricated classification')
    value.update(source=SOURCE,originalSource=value['source'],originalInventorySha256=selected.sha(original),
       qualificationSha256=selected.sha(qualified),classificationCounts=counts,
       newSiteReview=[{'path':'src/schubert-nk-storage/src/main/java/dev/codex/schubert/nk/storage/LinuxStartupAdmission.java',
           'method':'FdOwners.close','classification':'NON_APPLICABLE_PREBUILT_RELEASE',
           'reason':'Already-owned pair; no acquisition or callback construction between adoption and cleanup; both release fields constructed before adoption',
           'retestEvidence':'PG5150-native-fd-bytecode-v1/manifest.json and PT-OPS-CHILDFD-009/010'}],
       previousSource='d916dd96b9454fb012293c3e430688ce9c367a1b',
       newChangedPhysicalClasses=sorted(changed),addedPhysicalClasses=sorted(added),otherSamePhysicalClasses=755,
       wholeHorizontalComplete=False,acceptedLeafDelta=0,formalAccepted=False)
    out=root/'evidence/01_PT/003_NK-PRO-003/evidence/provisional/PG5154-scope-classification-native-v1'
    os.umask(0o077);out.mkdir(parents=True)
    with(out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'counts':counts,'newPrebuiltReleaseSites':1,'sha256':selected.sha(out/'manifest.json')}))


if __name__=='__main__':main()
