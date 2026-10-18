"""Original237 preserved,16 additional limited fixes; unresolved candidates remain explicit."""
import json
import os
import subprocess
import pg5146_scope_classification as inventory
import pg5168_release_selected as entry

SOURCE='1c45f4ec689d2796d271dc745b7d9cde1827a31b'
QUALIFIED='018_NK-OPS-001/evidence/provisional/pg5168-release-scopes-green-v1-metadata-v2/manifest.json'


def main():
    root=entry.selected.ROOT
    original=root/('evidence/01_PT/'+inventory.INVENTORY)
    if entry.selected.sha(original)!='9f9c80a5968d5f9a6010e98fa74854c17777c99076eb98d11e3f4e4129870344':
        raise ValueError('immutable original237 candidates')
    qualified=root/('evidence/01_PT/'+QUALIFIED);proof=json.loads(qualified.read_bytes())
    if proof['productionCandidateSource']!=SOURCE or proof['actualExit']!=0 or proof['tests']!=537 or proof['suites']!=73:
        raise ValueError('same-source qualified537/73')
    value=json.loads(original.read_bytes())
    counts=inventory.classify(value['files'],
       lambda path:subprocess.check_output(['git','show',SOURCE+':'+path],cwd=root),
       native=True,evidence_ref=QUALIFIED,extra_fixed={
         'NativeCoveragePrivateFile.java','ReleasePayloadVerification.java','StartupReleaseManifest.java'})
    if counts!={'FIXED_LIMITED':52,'NON_APPLICABLE_BORROWED':1,'UNKNOWN':184}:
        raise ValueError('complete original237 partition')
    old=json.loads((root/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5162-scope-classification-coverage-v1/manifest.json').read_bytes())
    value.update(source=SOURCE,originalSource=value['source'],originalInventorySha256=entry.selected.sha(original),
       qualificationSha256=entry.selected.sha(qualified),classificationCounts=counts,newSiteReview=old['newSiteReview'],
       newChangedOuterClasses=2,nestedDebugEquivalent=proof['nestedDebugEquivalent'],
       otherPhysicalClassesUnchanged=proof['otherPhysicalClassesUnchanged'],
       wholeHorizontalComplete=False,acceptedLeafDelta=0,formalAccepted=False)
    out=root/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5174-scope-classification-release-v1'
    os.umask(0o077);out.mkdir(parents=True)
    with(out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'counts':counts,'sha256':entry.selected.sha(out/'manifest.json')}))


if __name__=='__main__':main()
