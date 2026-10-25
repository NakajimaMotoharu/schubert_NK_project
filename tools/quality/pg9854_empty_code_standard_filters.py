"""Static pinned-library filter ranges for saved class bytes, not an executable coverage run."""
from collections import Counter
import json
import os
from pathlib import Path
import zipfile
import g07_host_class_provenance_inputs as data
import pg9346_direct_companion_jdk_post as steps
from host_tool_invocation import capture, verify

ROOT = data.ROOT
BASE = data.BASE
SOURCE = '8ba82083ec65abc6373b8454576dcbaee7d3e621'
SLOT = ROOT.parent/'pgpt-runs/PG379/pg9854-empty-code-standard-filters-v1'
OUT = BASE/'PG9854-empty-code-standard-filters-v1'


def main():
    invocation = capture(Path(__file__))
    assert not SLOT.exists() and not OUT.exists()
    structure_sha = 'a2b6e797428c46e7940de9e224d044b58c30233388d019c903e74fdce51876d4'
    structure = data.read_checked(BASE/'PG9848-main-code-structure-v2/manifest.json',structure_sha)
    rows = data.read_checked(BASE/'PG9848-main-code-structure-v2/class-structures.json',structure['classStructuresSha256'])
    normal = data.read_checked(BASE/'PG9812-cleanup-values-six-compile-v1/manifest.json',structure['normalManifestSha256'])
    old_proof = data.read_checked(ROOT/'evidence/01_PT/002_NK-PRO-002/evidence/provisional/PG9842-protocol-switchmap-review-v2/manifest.json',
        '4159dc3dda26a447e147b3c689de36e2052662fada0d9a87374a5fec4b208bed')
    assert structure['actualExit'] == normal['actualExit'] == 0 and structure['source'] == normal['source'] == SOURCE
    selected = {r['physicalKey']:r for r in rows if r['historicalSha256'] is not None and not r['historicalCounters']
        and r['structureStatus'] in ('CODE_PRESENT_NOT_RUNTIME_QUALIFICATION','SYNTHETIC_CODE_REQUIRES_APPLICABILITY_REVIEW')}
    assert len(selected) == 31 and sum(sum(m['hasCode'] for m in r['structure']['methods']) for r in selected.values()) == 49
    libraries = old_proof['libraryHashes']
    assert len(libraries) == 4 and all(data.sha(Path(p).read_bytes()) == h for p,h in libraries.items())
    helper = ROOT/'tools/quality/architecture/EmptyCounterStandardFilterAudit.java'
    helper_sha = data.sha(helper.read_bytes())
    assert all(data.sha(Path(j['path']).read_bytes()) == j['sha256'] for j in normal['jars'].values())
    os.umask(0o077)
    SLOT.mkdir()
    classes = SLOT/'reader'
    classes.mkdir()
    catalog = SLOT/'jars.tsv'
    with catalog.open('x') as stream:
        stream.write(''.join(m+'\t'+j['path']+'\n' for m,j in sorted(normal['jars'].items())))
    targets = SLOT/'targets.txt'
    with targets.open('x') as stream:
        stream.write(''.join(k+'\n' for k in sorted(selected)))
    tc = ROOT.parent/'toolchain/jdk-25.0.4/bin'
    classpath = ':'.join(libraries)
    steps.SLOT = SLOT
    stages = [steps.step('compile-static-reader',[str(tc/'javac'),'--release','25','-proc:none','-Xlint:all','-Werror',
        '-cp',classpath,'-d',str(classes),str(helper)])]
    assert stages[0]['actualExit'] == 0 and not stages[0]['timedOut']
    stages.append(steps.step('standard-filter-ranges',[str(tc/'java'),'-cp',str(classes)+':'+classpath,helper.stem,str(catalog),str(targets)]))
    assert stages[-1]['actualExit'] == 0 and not stages[-1]['timedOut']
    methods,observed = [],{}
    text = (SLOT/'standard-filter-ranges.stdout').read_text()
    lines = text.splitlines()
    assert lines[-1] == 'TOTAL\t31\t49'
    for line in lines[:-1]:
        f = line.split('\t')
        if f[0] == 'CLASS':
            assert len(f) == 4 and f[1] in selected and f[1] not in observed
            observed[f[1]] = dict(superName=f[2],asmFlags=int(f[3]))
        else:
            assert f[0] == 'METHOD' and len(f) == 7 and f[1] in selected
            original = next(m for m in selected[f[1]]['structure']['methods'] if (m['name'],m['descriptor']) == (f[2],f[3]))
            assert original['hasCode'] and original['flags'] == int(f[4])
            total,ignored = int(f[5]),int(f[6])
            assert total > 0 and total == ignored
            methods.append(dict(physicalKey=f[1],name=f[2],descriptor=f[3],methodFlags=int(f[4]),
                realOpcodeInstructions=total,standardFilterIgnoredOpcodes=ignored,remainingOpcodes=total-ignored,
                originalCodeLength=original['codeLength'],classSha256=selected[f[1]]['currentSha256']))
    assert set(observed) == set(selected) and len(methods) == len({(m['physicalKey'],m['name'],m['descriptor']) for m in methods}) == 49
    # Bind target entries after parsing; target classes are never on the executable classpath.
    for module,j in normal['jars'].items():
        with zipfile.ZipFile(j['path']) as jar:
            for key,row in selected.items():
                if key.startswith(module+':'):
                    assert data.sha(jar.read(key.split(':',1)[1])) == row['currentSha256']
    assert data.sha(helper.read_bytes()) == helper_sha
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in normal['begin']['inputHashes'].items())
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'method-filter-ranges.json',methods)
    data.write(OUT/'class-filter-contexts.json',observed)
    (OUT/'standard-filter-ranges.txt').write_text(text)
    result = dict(actualExit=0,source=SOURCE,invocation=invocation,structureManifestSha256=structure_sha,
        normalManifestSha256=structure['normalManifestSha256'],libraryHashes=libraries,helperSha256=helper_sha,stages=stages,
        classes=31,codeMethods=49,remainingOpcodeInstructions=sum(m['remainingOpcodes'] for m in methods),
        opcodeInstructions=sum(m['realOpcodeInstructions'] for m in methods),
        methodNameCounts=dict(Counter(m['name'] for m in methods)),
        methodRangesSha256=data.sha((OUT/'method-filter-ranges.json').read_bytes()),
        contextsSha256=data.sha((OUT/'class-filter-contexts.json').read_bytes()),
        targetClasspathContainsProduct=False,targetDefinedOrInitialized=False,productTestsExecuted=0,
        newExclusionSettings=False,exclusionReviewApprovalGranted=False,currentCoverageComputed=False,
        rawMissedProbesRewritten=False,historicalSuccessTransferred=False,newAccepted=0,formalUpdated=False,
        wholeG01Accepted=False,whole451Accepted=False,effortPercent=None)
    data.write(OUT/'manifest.json',result)
    print(json.dumps(dict(actualExit=0,classes=31,methods=49,opcodes=result['opcodeInstructions'],remaining=0,
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
