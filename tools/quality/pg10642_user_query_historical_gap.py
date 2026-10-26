"""Read original exec and exact historical class only; no new PT/coverage run."""
import json
import os
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9346_direct_companion_jdk_post as steps

SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg10642-user-query-historical-gap-v1'
OUT = data.BASE/'PG10642-user-query-historical-gap-v1'


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    original_path = data.BASE/'PG9974-plain-core-fixed-post-v1/manifest.json'
    original = data.read_checked(original_path,'7e37b3f71ef9716661798c908ec231c45a2883cbe0e97df55dbbee13c1a7fe5b')
    assert original['source'] == '70165b0768a1fabd13371cc25a55978fcf3452ba' and original['actualExit'] == 0
    work = data.ROOT.parent/'pgpt-runs/PG379'
    execution = work/'pg9972-plain-core-fixed-host-v1/jacoco.exec'
    name = 'dev/codex/schubert/nk/api/application/admin/UserQueryRequest.class'
    unit = work/'pg9974-plain-core-fixed-post-v1/complete-codec'/name
    assert data.sha(execution.read_bytes()) == original['execSha256']
    assert data.sha(unit.read_bytes()) == original['physicalMainClasses'][name]
    helper = data.ROOT/'tools/quality/architecture/UserQueryHistoricalGapMetadata.java'
    helper_sha = data.sha(helper.read_bytes())
    libs = original['libraryHashes']
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in libs.items())
    tc = data.ROOT.parent/'toolchain'
    cp = os.pathsep.join(libs)
    SLOT.mkdir()
    reader = SLOT/'reader'
    reader.mkdir()
    steps.SLOT = SLOT
    stages = [steps.step('compile-reader',[str(tc/'jdk-25.0.4/bin/javac'),'--release','25',
        '-proc:none','-Xlint:all','-Werror','-cp',cp,'-d',str(reader),str(helper)])]
    assert stages[0]['actualExit'] == 0 and not stages[0]['timedOut']
    stages.append(steps.step('read-old-counters',[str(tc/'jdk-25.0.4/bin/java'),'-cp',str(reader)+os.pathsep+cp,
        helper.stem,str(execution),str(unit)]))
    assert stages[-1]['actualExit'] == 0 and not stages[-1]['timedOut']
    text = (SLOT/'read-old-counters.stdout').read_text()
    lines = text.splitlines()
    assert lines[0] == 'CLASS\t'+name.removesuffix('.class')+'\t'+original['classCrc64']
    methods = []
    for line in lines[1:]:
        tag,method,descriptor,*values = line.split('\t')
        assert tag == 'METHOD' and len(values) == 4
        counters = {}
        for label,value in zip(('LINE','METHOD','CLASS','BRANCH'),values):
            missed,covered = map(int,value.split('/'))
            counters[label] = dict(missed=missed,covered=covered)
        methods.append(dict(method=method,descriptor=descriptor,counters=counters))
    for label,counter in original['counters'].items():
        if label != 'CLASS':
            assert sum(m['counters'][label]['missed'] for m in methods) == counter['missed']
            assert sum(m['counters'][label]['covered'] for m in methods) == counter['covered']
    assert data.sha(helper.read_bytes()) == helper_sha
    assert data.sha(execution.read_bytes()) == original['execSha256'] and data.sha(unit.read_bytes()) == original['physicalMainClasses'][name]
    assert all(data.sha(Path(p).read_bytes()) == h for p,h in libs.items())
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'methods.json',methods)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original['source'],invocation=invocation,
        originalManifestSha256=data.sha(original_path.read_bytes()),originalExecSha256=original['execSha256'],
        originalClassSha256=original['physicalMainClasses'][name],classCrc64=original['classCrc64'],
        helperSha256=helper_sha,dependencyHashes=libs,stages=stages,methodsSha256=data.sha((OUT/'methods.json').read_bytes()),
        coverageQualification='HISTORICAL_GAP_METADATA_ONLY_NOT_CURRENT_SOURCE_PT',
        targetClassLoaded=False,productTestsExecuted=0,newMeasuredCoverage=False,externalActions=0,
        oldRuntimeReassigned=False,newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,methods=len(methods),missing=[m['method'] for m in methods if m['counters']['METHOD']['missed']],
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
