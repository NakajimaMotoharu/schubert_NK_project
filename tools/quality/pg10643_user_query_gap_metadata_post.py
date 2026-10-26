"""Recover original reader output only; never recompile/replay reader or target Tests."""
import json
from pathlib import Path
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

OUT = data.BASE/'PG10643-user-query-gap-metadata-post-v1'
RAW_SHA = 'fdbffee251dc881d6309b9477ee0b3e79ef4d57e278de58a67aa0fe861d44ebc'


def parse(raw,original):
    if data.sha(raw) != RAW_SHA:
        raise ValueError('exact original existing stdout required')
    lines = raw.decode().splitlines()
    if lines[0] != 'CLASS\tdev/codex/schubert/nk/api/application/admin/UserQueryRequest\t'+original['classCrc64']:
        raise ValueError('historical class CRC required')
    methods = []
    for line in lines[1:]:
        tag,name,descriptor,*values = line.split('\t')
        if tag != 'METHOD' or len(values) != 4:
            raise ValueError('method counters schema')
        counters = {label:dict(zip(('missed','covered'),map(int,value.split('/'))))
                    for label,value in zip(('LINE','METHOD','CLASS','BRANCH'),values)}
        methods.append(dict(method=name,descriptor=descriptor,counters=counters))
    if len(methods) != 13 or len({(m['method'],m['descriptor']) for m in methods}) != 13:
        raise ValueError('all thirteen original methods')
    for label in ('METHOD','BRANCH'):
        for state in ('missed','covered'):
            if sum(m['counters'][label][state] for m in methods) != original['counters'][label][state]:
                raise ValueError('method and branch aggregate match original')
    return methods


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    original_path = data.BASE/'PG9974-plain-core-fixed-post-v1/manifest.json'
    original = data.read_checked(original_path,'7e37b3f71ef9716661798c908ec231c45a2883cbe0e97df55dbbee13c1a7fe5b')
    assert original['source'] == '70165b0768a1fabd13371cc25a55978fcf3452ba' and original['actualExit'] == 0
    work = data.ROOT.parent/'pgpt-runs/PG379'
    execution = work/'pg9972-plain-core-fixed-host-v1/jacoco.exec'
    name = 'dev/codex/schubert/nk/api/application/admin/UserQueryRequest.class'
    unit = work/'pg9974-plain-core-fixed-post-v1/complete-codec'/name
    assert data.sha(execution.read_bytes()) == original['execSha256']
    assert data.sha(unit.read_bytes()) == original['physicalMainClasses'][name]
    failed_tool = data.ROOT/'tools/quality/pg10642_user_query_historical_gap.py'
    assert data.sha(failed_tool.read_bytes()) == '477c5c0153d5b652f644dc605557e5d19f63e4d6be5e03de230928b98fe2dfa6'
    raw = (work/'pg10642-user-query-historical-gap-v1/read-old-counters.stdout').read_bytes()
    methods = parse(raw,original)
    missing = [m for m in methods if m['counters']['METHOD']['missed']]
    assert len(missing) == 1 and missing[0]['method'] == 'query'
    assert missing[0]['counters']['LINE'] == dict(missed=8,covered=0)
    assert missing[0]['counters']['BRANCH'] == dict(missed=2,covered=0)
    rejected = []
    for label,altered in [('crc',raw.replace(original['classCrc64'].encode(),b'0'*16,1)),
                          ('missing-row',raw[:raw.rfind(b'METHOD\t')]),
                          ('counter',raw.replace(b'\t8/0\t1/0',b'\t0/8\t1/0',1))]:
        assert altered != raw
        try:
            parse(altered,original)
        except ValueError:
            rejected.append(label)
        else:
            raise AssertionError('altered historical metadata accepted')
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'methods.json',methods)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=original['source'],invocation=invocation,
        originalManifestSha256=data.sha(original_path.read_bytes()),originalExecSha256=original['execSha256'],
        originalClassSha256=original['physicalMainClasses'][name],classCrc64=original['classCrc64'],
        originalReaderStdoutSha256=RAW_SHA,originalToolSha256=data.sha(failed_tool.read_bytes()),
        methodsSha256=data.sha((OUT/'methods.json').read_bytes()),originalClassCounters=original['counters'],
        methodLineSums={s:sum(m['counters']['LINE'][s] for m in methods) for s in ('missed','covered')},
        missingMethods=missing,metadataNegativeVectors=rejected,
        sourceLineOverlapNotSummedIntoClass=True,readerReexecuted=False,targetClassLoaded=False,
        coverageQualification='HISTORICAL_GAP_METADATA_ONLY_NOT_CURRENT_SOURCE_PT',
        nextDependency='NORMAL_QUERY_REPOSITORY_CONNECTION_SQL_HOLD_NOT_A_NEW_PURE_GAP',
        productTestsExecuted=0,newMeasuredCoverage=False,externalActions=0,oldRuntimeReassigned=False,
        newAccepted=0,formalUpdated=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0,missingMethods=['query'],productTestsExecuted=0,
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
