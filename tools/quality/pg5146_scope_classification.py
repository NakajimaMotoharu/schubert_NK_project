"""Carry original 237 candidates; credit only explicit per-file limited evidence or borrowed proof."""
import hashlib
import json
import os
import subprocess
import pg5120_root_elf_selected as selected

SOURCE='d916dd96b9454fb012293c3e430688ce9c367a1b'
PREFIX='evidence/01_PT/'
INVENTORY='003_NK-PRO-003/evidence/provisional/PG5134-scope-candidate-inventory-v1/manifest.json'
QUALIFIED='018_NK-OPS-001/evidence/provisional/pg5140-storage-callers-green-v3-metadata-v2/manifest.json'
ROOT_FIXED={'RootServiceExecutableAdmission.java','RootStartupPending.java','OwnedTransferDirectory.java'}
CALLER_FIXED={'StorageRootInspection.java','ExistingFileAccess.java','ServiceConfigFiles.java','LinuxFilesystemClassifier.java'}


def classify(rows,load,*,native=False,evidence_ref=QUALIFIED,extra_fixed=frozenset()):
    counts={'FIXED_LIMITED':0,'NON_APPLICABLE_BORROWED':0,'UNKNOWN':0}
    seen=set()
    native_fixed={'LinuxFileLock.java','LinuxSealedProof.java','LinuxStartupAdmission.java'} if native else set()
    for row in rows:
        name=row['path'].rpartition('/')[2];content=load(row['path'])
        if name in ROOT_FIXED|CALLER_FIXED|native_fixed|extra_fixed:
            seen.add(name)
            prebuilt=native and name=='LinuxStartupAdmission.java' and content.count(b'ResourceScope.use(')==1 and b'ResourceScope.use(admissionRelease, proofRelease);' in content
            if b'ResourceScope.use(' in content and not prebuilt:raise ValueError('claimed fixed file still has original scope candidates')
            classification='FIXED_LIMITED'
            reason='Acquire/release/action before ownership; wrapper preallocation and protected helper; exact current222/bytecode'
        elif name=='LinuxExecDescriptors.java':
            seen.add(name);classification='NON_APPLICABLE_BORROWED'
            reason='Borrowed descriptor flags remain unchanged before scope; no resource acquisition; set under protection'
            if content.count(b'ResourceScope.use(')!=1:raise ValueError('exact borrowed scope')
        else:
            classification='UNKNOWN';reason=None
            if hashlib.sha256(content).hexdigest()!=row['sourceSha256']:
                raise ValueError('unreviewed original source changed; never carry stale unknown')
        for site in row['sites']:
            site.update(classification=classification,fixedLimited=classification=='FIXED_LIMITED',
                        fixed=False,nonApplicableReason=reason if classification=='NON_APPLICABLE_BORROWED' else None,
                        reviewReason=reason,retestEvidence=evidence_ref if classification!='UNKNOWN' else None)
            counts[classification]+=1
    if seen!=ROOT_FIXED|CALLER_FIXED|native_fixed|extra_fixed|{'LinuxExecDescriptors.java'}:raise ValueError('all explicitly reviewed original files')
    return counts


def main():
    original=selected.ROOT/(PREFIX+INVENTORY);qualified=selected.ROOT/(PREFIX+QUALIFIED)
    if selected.sha(original)!='9f9c80a5968d5f9a6010e98fa74854c17777c99076eb98d11e3f4e4129870344':
        raise ValueError('original inventory immutable')
    proof=json.loads(qualified.read_bytes())
    if proof['productionCandidateSource']!=SOURCE or proof['actualExit']!=0:
        raise ValueError('exact current-source qualification')
    value=json.loads(original.read_bytes())
    counts=classify(value['files'],lambda p:subprocess.check_output(['git','show',SOURCE+':'+p],cwd=selected.ROOT))
    if counts!={'FIXED_LIMITED':22,'NON_APPLICABLE_BORROWED':1,'UNKNOWN':214}:raise ValueError('all237 original sites partitioned')
    value.update(source=SOURCE,originalSource=value['source'],originalInventorySha256=selected.sha(original),
                 qualificationSha256=selected.sha(qualified),classificationCounts=counts,
                 wholeHorizontalComplete=False,acceptedLeafDelta=0,formalAccepted=False,
                 note='fixedLimited is not formal fixed/leaf close; unknown candidates are not assumed defects')
    out=selected.ROOT/(PREFIX+'003_NK-PRO-003/evidence/provisional/PG5146-scope-classification-v1')
    os.umask(0o077);out.mkdir(parents=True)
    with(out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'counts':counts,'sha256':selected.sha(out/'manifest.json'),'horizontalComplete':False}))


if __name__=='__main__':main()
