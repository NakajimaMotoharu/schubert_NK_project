"""Fresh namespaced document references; preserve every legacy marker and the original writer."""
import copy
import difflib
import json
import sys
import pg12458_config_template_trace as original
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9954_pure_query_registry_metadata import replaced
from pg9338_wbs_reference_metadata_post import validate
from pg9880_snapshot_nonce_trace import audit

OUT = data.BASE/'PG12461-config-template-trace-post-v2'
REGISTRY = '95d2b841403afa883e9c99e4cbfa903f2e14d46131e72b7a75a0addbd179b425'
PREVIOUS = 'previousConfigTemplateSevenPG12458RegistryReference'
BINDING = 'currentConfigTemplateSevenPG12458BindingReference'

def documents(raw,snap):
    for name in original.SECTIONS:
        section = json.loads(raw)[name]
        assert PREVIOUS not in section and BINDING not in section
        section[PREVIOUS] = {k:copy.deepcopy(section[k]) for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        section.update(source=original.SOURCE,manifest=str((original.OUT/'manifest.json').relative_to(data.ROOT)),sha256=REGISTRY,record='evidence/01_PT/018_NK-OPS-001/2337_公開設定Template七指摘_製造単体結果.md',currentAddedTestPaths=[])
        section[BINDING] = dict(manifest=str((original.OUT/'manifest.json').relative_to(data.ROOT)),sha256=REGISTRY,objectPath='currentPublicTemplateFixtureBinding',qualification='SOURCE_BOUND_7_SAMEVALUE_FIXES_INVERSE22_ORIGINAL4_PUBLIC_RESOURCES7_NO_MAIN_EXECUTION')
        if name == original.SECTIONS[0]:
            section.update(independentPostManifest=str((OUT/'manifest.json').relative_to(data.ROOT)),independentPostSha256=None)
        else:
            section.update(guardManifest=str((OUT/'manifest.json').relative_to(data.ROOT)),guardSha256=None)
        raw,_,_ = replaced(raw,name,section)
    snap,_,_ = replaced(snap,'inventorySha256',data.sha(raw))
    return raw,snap

def emit():
    _,_,_,raw,snap = original.inputs()
    assert (data.ROOT/original.INV).read_bytes() == raw and (data.ROOT/original.SNAP).read_bytes() == snap
    after,after_snap = documents(raw,snap);patch = '*** Begin Patch\n'
    for name,a,b in ((original.INV,raw,after),(original.SNAP,snap,after_snap)):
        patch += '*** Update File: '+str(data.ROOT/name)+'\n'+'\n'.join('@@' if l.startswith('@@') else l for l in list(difflib.unified_diff(a.decode().splitlines(),b.decode().splitlines(),n=0))[2:])+'\n'
    return patch+'*** End Patch\n'

def main():
    invocation = capture(__file__);assert not OUT.exists() and not original.POST.exists()
    prior,proof,plan,raw,snap = original.inputs()
    value = data.read_checked(original.OUT/'manifest.json',REGISTRY)
    reference = original.expected(prior,proof,plan,raw)
    def require(candidate):
        if any(candidate.get(k) != v for k,v in reference.items()):
            raise ValueError('exact C06 source/owner/host-only qualification required')
    require(value);after,after_snap = documents(raw,snap)
    assert (data.ROOT/original.INV).read_bytes() == after and (data.ROOT/original.SNAP).read_bytes() == after_snap
    old,new = json.loads(raw),json.loads(after)
    replaced_keys = {'source','manifest','sha256','record','currentAddedTestPaths','independentPostManifest','independentPostSha256','guardManifest','guardSha256'}
    for name in original.SECTIONS:
        assert new[name][PREVIOUS] == {k:old[name][k] for k in ('source','manifest','sha256','record','currentAddedTestPaths')}
        assert all(new[name][k] == v for k,v in old[name].items() if k not in replaced_keys)
        assert new[name]['previousPublicTemplateRegistryReference'] == old[name]['previousPublicTemplateRegistryReference']
    validate(after,after_snap,old,json.loads(snap));labels = []
    for key,wrong in [('canonicalOwner','WBS-F03'),('canonicalCostOwner','WBS-F02'),('sha256','0'*64)]:
        bad = copy.deepcopy(reference);row = bad['currentPublicTemplateFixtureBinding']['sourceChanges'][0]
        assert row[key] != wrong;row[key] = wrong
        try:
            require(bad)
        except ValueError:
            labels.append(key)
        else:
            raise AssertionError('invalid source/owner accepted')
    for key,wrong in [('observedTestExecutions',3),('productMainExecuted',True),('oldExecUnion',True)]:
        bad = copy.deepcopy(reference);row = bad['currentPublicTemplateHostQualification']
        assert row[key] != wrong;row[key] = wrong
        try:
            require(bad)
        except ValueError:
            labels.append(key)
        else:
            raise AssertionError('invalid runtime qualification accepted')
    observed = audit();assert observed['actualExit'] == 1 and observed['lastError'] == value['wholeWbsAuditBefore']['lastError']
    verify(invocation);OUT.mkdir();data.write(OUT/'manifest.json',dict(actualExit=0,source=original.SOURCE,invocation=invocation,registryManifestSha256=REGISTRY,inventorySha256=data.sha(after),snapshotSha256=data.sha(after_snap),freshNamespaceKeys=[PREVIOUS,BINDING],legacyNamespacePreserved=True,originalEmitterObservedExit=None,originalEmissionResponseMissing=True,oldPostNotExecuted=True,oldRowsChangedShaOnly=1,allOtherPriorRowsUnchanged=982,metadataNegativeVectors=len(labels),nonVacuousNegativeLabels=labels,wholeWbsAuditBefore=value['wholeWbsAuditBefore'],wholeWbsAuditAfter=observed,productTestsExecuted=0,coverage=None,whole451Accepted=False,wholeF03Accepted=False,newAccepted=0,effortPercent=None,relatedBugs=['BUG-1975'],relatedYkt=['YKT-1723']));print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':
    if sys.argv[1:] == ['--emit-patch']:
        print(emit(),end='')
    else:
        assert not sys.argv[1:];main()
