"""Independent source-owner/cost post: six non-vacuous negatives, no Product replay."""
import copy
import difflib
import json
import sys
import pg12418_batch_runtime_trace as original
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9954_pure_query_registry_metadata import replaced
from pg9338_wbs_reference_metadata_post import validate
from pg9880_snapshot_nonce_trace import audit

OUT = data.BASE/'PG12421-batch-runtime-trace-post-v2'
REGISTRY = 'e216153b1e7151ef811c19aa839e1d3aa6f4b0f74bd0ea929d199bed94bbc85f'

def documents(raw,snap):
    prior,prior_snap,_,_ = original.documents(raw,snap)
    after = prior
    for name in original.SECTIONS:
        section = json.loads(after)[name]
        key = 'independentPostManifest' if name == original.SECTIONS[0] else 'guardManifest'
        assert section[key] == str((original.POST/'manifest.json').relative_to(data.ROOT))
        section[key] = str((OUT/'manifest.json').relative_to(data.ROOT))
        after,_,_ = replaced(after,name,section)
    after_snap,_,_ = replaced(prior_snap,'inventorySha256',data.sha(after))
    return prior,prior_snap,after,after_snap

def emit():
    _,_,_,(raw,snap) = original.inputs();prior,prior_snap,after,after_snap = documents(raw,snap)
    assert (data.ROOT/original.INV).read_bytes() == prior and (data.ROOT/original.SNAP).read_bytes() == prior_snap
    patch = '*** Begin Patch\n'
    for name,before,result in ((original.INV,prior,after),(original.SNAP,prior_snap,after_snap)):
        lines = list(difflib.unified_diff(before.decode().splitlines(),result.decode().splitlines(),n=0))[2:]
        patch += '*** Update File: '+str(data.ROOT/name)+'\n'+'\n'.join('@@' if line.startswith('@@') else line for line in lines)+'\n'
    return patch+'*** End Patch\n'

def main():
    invocation = capture(__file__);assert not OUT.exists() and not original.POST.exists()
    prior,proof,plan,(raw,snap) = original.inputs()
    value = data.read_checked(original.OUT/'manifest.json',REGISTRY)
    reference = original.expected(prior,proof,plan);original.contract(value,reference)
    before,before_snap,after,after_snap = documents(raw,snap)
    assert (data.ROOT/original.INV).read_bytes() == after and (data.ROOT/original.SNAP).read_bytes() == after_snap
    validate(after,after_snap,json.loads(raw),json.loads(snap))
    vectors = []
    for field,wrong in [('canonicalOwner','WBS-G13.07'),('canonicalCostOwner','WBS-F03'),('sha256','0'*64)]:
        bad = copy.deepcopy(reference);binding = bad['currentBatchRuntimeOracleBinding']['sourceChanges'][0]
        assert binding[field] != wrong;binding[field] = wrong;vectors.append((field,bad))
    for field,wrong in [('oldExecUnion',True),('observedTestExecutions',2),('wholeArtifactsFourCounters100',True)]:
        bad = copy.deepcopy(reference);qualification = bad['currentBatchRuntimeOracleRuntimeQualification']
        assert qualification[field] != wrong;qualification[field] = wrong;vectors.append((field,bad))
    for label,bad in vectors:
        assert bad != reference
        try:
            original.contract(bad,reference)
        except ValueError:
            pass
        else:
            raise AssertionError('non-vacuous invalid metadata accepted: '+label)
    observed = audit()
    assert observed['actualExit'] == 1 and observed['lastError'] == value['wholeWbsAuditBefore']['lastError']
    verify(invocation);OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,registryManifestSha256=REGISTRY,inventorySha256=data.sha(after),snapshotSha256=data.sha(after_snap),referenceRepair=dict(beforeInventorySha256=data.sha(before),beforeSnapshotSha256=data.sha(before_snap),oldPostPath=str(original.POST.relative_to(data.ROOT)),newPostPath=str(OUT.relative_to(data.ROOT)),onlyPostReferencesAndInventoryHash=True),metadataNegativeVectors=len(vectors),nonVacuousNegativeLabels=[label for label,_ in vectors],wholeWbsAuditAfter=observed,registered=1808,javaPaths=1810,unknown=2,oldRowsChangedShaOnly=1,allOtherPriorRowsUnchanged=982,productTestsExecuted=0,coverage=None,whole451Accepted=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None,relatedBugs=['BUG-1973'],relatedYkt=['YKT-1721']))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:];main()
