"""Original inventory retained; seven additional fixed scopes backed by current536/bytecode."""
import json
import os
import subprocess
import pg5146_scope_classification as inventory
import pg5156_native_coverage_selected as entry

SOURCE='178b8d6d9d17bd610953ba1f2122e970af2d174b'
QUALIFIED='018_NK-OPS-001/evidence/provisional/pg5156-native-coverage-green-v2-metadata-v2/manifest.json'


def main():
    root=entry.selected.ROOT
    original=root/('evidence/01_PT/'+inventory.INVENTORY)
    if entry.selected.sha(original)!='9f9c80a5968d5f9a6010e98fa74854c17777c99076eb98d11e3f4e4129870344':
        raise ValueError('immutable original237 candidates')
    qualified=root/('evidence/01_PT/'+QUALIFIED);proof=json.loads(qualified.read_bytes())
    if proof['productionCandidateSource']!=SOURCE or proof['actualExit']!=0 or proof['tests']!=536 or proof['suites']!=73:
        raise ValueError('same-source current qualification')
    value=json.loads(original.read_bytes())
    counts=inventory.classify(value['files'],
       lambda path:subprocess.check_output(['git','show',SOURCE+':'+path],cwd=root),
       native=True,evidence_ref=QUALIFIED,extra_fixed={'NativeCoveragePrivateFile.java'})
    if counts!={'FIXED_LIMITED':36,'NON_APPLICABLE_BORROWED':1,'UNKNOWN':200}:
        raise ValueError('all237 rows retained without implicit unknown credit')
    old=json.loads((root/'evidence/01_PT/003_NK-PRO-003/evidence/provisional/PG5154-scope-classification-native-v1/manifest.json').read_bytes())
    value.update(source=SOURCE,originalSource=value['source'],originalInventorySha256=entry.selected.sha(original),
       qualificationSha256=entry.selected.sha(qualified),classificationCounts=counts,newSiteReview=old['newSiteReview'],
       targetClassFourCounters=proof['targetCoverageClassCounters'],targetClassFour100=proof['targetClassFour100'],
       previousSource='86ea5a200bf6cbe5a8d9e79c5cc962ec029a7307',newChangedPhysicalClasses=1,
       otherPhysicalClassesByteIdentical=763,wholeHorizontalComplete=False,acceptedLeafDelta=0,formalAccepted=False)
    out=root/'evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG5162-scope-classification-coverage-v1'
    os.umask(0o077);out.mkdir(parents=True)
    with(out/'manifest.json').open('x') as f:
        json.dump(value,f,ensure_ascii=False,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    print(json.dumps({'counts':counts,'sha256':entry.selected.sha(out/'manifest.json')}))


if __name__=='__main__':main()
