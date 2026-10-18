"""Original237 rows kept with13 newly evidenced environment sites, never blanket defect/acceptance."""
import json
import os
import subprocess
import pg5146_scope_classification as inventory
import pg5184_environment_selected as entry

SOURCE='8f8c813c95cf3331d9f49535a83bae98b1f3fd2c'
QUALIFIED='018_NK-OPS-001/evidence/provisional/pg5184-environment-scopes-green-v1-metadata-v2/manifest.json'


def main():
    root=entry.selected.ROOT
    original=root/('evidence/01_PT/'+inventory.INVENTORY)
    if entry.selected.sha(original)!='9f9c80a5968d5f9a6010e98fa74854c17777c99076eb98d11e3f4e4129870344':
        raise ValueError('immutable original237 candidates')
    qualified=root/('evidence/01_PT/'+QUALIFIED);proof=json.loads(qualified.read_bytes())
    if proof['productionCandidateSource']!=SOURCE or proof['actualExit']!=0 or proof['tests']!=642 or proof['suites']!=81:
        raise ValueError('same-source qualified642/81')
    value=json.loads(original.read_bytes())
    counts=inventory.classify(value['files'],
       lambda path:subprocess.check_output(['git','show',SOURCE+':'+path],cwd=root),
       native=True,evidence_ref=QUALIFIED,extra_fixed={
         'NativeCoveragePrivateFile.java','ReleasePayloadVerification.java','StartupReleaseManifest.java',
         'BackupArtifactVerifier.java','BackupManifestPublisher.java','BackupManifestReader.java',
         'InspectorEnvironmentFiles.java','InspectorEnvironmentReader.java','InspectorEnvironmentPublisher.java'})
    if counts!={'FIXED_LIMITED':84,'NON_APPLICABLE_BORROWED':1,'UNKNOWN':152}:
        raise ValueError('complete original237 partition')
    old=json.loads((root/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5182-scope-classification-backup-v1/manifest.json').read_bytes())
    value.update(source=SOURCE,originalSource=value['source'],originalInventorySha256=entry.selected.sha(original),
       qualificationSha256=entry.selected.sha(qualified),classificationCounts=counts,newSiteReview=old['newSiteReview'],
       checkedNullIoFactories=3,newChangedOuterClasses=3,nestedDebugEquivalent=proof['nestedDebugEquivalent'],
       otherPhysicalClassesUnchanged=proof['otherPhysicalClassesUnchanged'],
       wholeHorizontalComplete=False,acceptedLeafDelta=0,formalAccepted=False)
    out=root/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5190-scope-classification-environment-v1'
    os.umask(0o077);out.mkdir(parents=True)
    with(out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'counts':counts,'sha256':entry.selected.sha(out/'manifest.json')}))


if __name__=='__main__':main()
