"""Original237 rows preserved;19 Backup scopes become limited fixes only after same-source611."""
import json
import os
import subprocess
import pg5146_scope_classification as inventory
import pg5176_backup_selected as entry

SOURCE='2a56f0319b25493b34434afe965dad558347f720'
QUALIFIED='018_NK-OPS-001/evidence/provisional/pg5176-backup-scopes-green-v1-metadata-v2/manifest.json'


def main():
    root=entry.selected.ROOT
    original=root/('evidence/01_PT/'+inventory.INVENTORY)
    if entry.selected.sha(original)!='9f9c80a5968d5f9a6010e98fa74854c17777c99076eb98d11e3f4e4129870344':
        raise ValueError('immutable original237 candidates')
    qualified=root/('evidence/01_PT/'+QUALIFIED);proof=json.loads(qualified.read_bytes())
    if proof['productionCandidateSource']!=SOURCE or proof['actualExit']!=0 or proof['tests']!=611 or proof['suites']!=78:
        raise ValueError('same-source qualified611/78')
    value=json.loads(original.read_bytes())
    counts=inventory.classify(value['files'],
       lambda path:subprocess.check_output(['git','show',SOURCE+':'+path],cwd=root),
       native=True,evidence_ref=QUALIFIED,extra_fixed={
         'NativeCoveragePrivateFile.java','ReleasePayloadVerification.java','StartupReleaseManifest.java',
         'BackupArtifactVerifier.java','BackupManifestPublisher.java','BackupManifestReader.java'})
    if counts!={'FIXED_LIMITED':71,'NON_APPLICABLE_BORROWED':1,'UNKNOWN':165}:
        raise ValueError('complete original237 partition')
    old=json.loads((root/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5174-scope-classification-release-v1/manifest.json').read_bytes())
    value.update(source=SOURCE,originalSource=value['source'],originalInventorySha256=entry.selected.sha(original),
       qualificationSha256=entry.selected.sha(qualified),classificationCounts=counts,newSiteReview=old['newSiteReview'],
       checkedNullIoFactories=7,newChangedOuterClasses=3,nestedDebugEquivalent=proof['nestedDebugEquivalent'],
       otherPhysicalClassesUnchanged=proof['otherPhysicalClassesUnchanged'],
       wholeHorizontalComplete=False,acceptedLeafDelta=0,formalAccepted=False)
    out=root/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5182-scope-classification-backup-v1'
    os.umask(0o077);out.mkdir(parents=True)
    with(out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'counts':counts,'sha256':entry.selected.sha(out/'manifest.json')}))


if __name__=='__main__':main()
