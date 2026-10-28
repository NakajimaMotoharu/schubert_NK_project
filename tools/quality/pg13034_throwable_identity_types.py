"""Closed read-only Main diagnostic typing; no Product class loading/generation or PT."""
from collections import Counter
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg13026_http_route_name_context import state_after
from pg9954_pure_query_registry_metadata import INV
import trace_owner_join as ownership
import pg9666_pagination_static as runner

SOURCE = '2f4290e7e511ea30224d087f78d44964d3488919'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13034-throwable-identity-types-v1'
OUT = data.BASE/'PG13034-throwable-identity-types-v1'

def main():
    invocation = capture(__file__); assert not SLOT.exists() and not OUT.exists()
    normal = data.read_checked(data.BASE/'PG13018-http-route-name-six-compile-v1/manifest.json','66360a6446a271767118ed3ff4d734701f55a010638dc7676490409a0c488351')
    host = data.read_checked(data.BASE/'PG13020-http-route-name-host-v1/manifest.json','647c3c5306e93d3402c8fc135e5ecfe1acf4a4dab245d4488d7e39e76cd561f4')
    assert normal['source'] == host['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == host['actualExit'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in hashes.items())
    original_path = data.BASE/'PG10690-current-global-static-post-v1/findings.json'
    original_raw = original_path.read_bytes(); original = json.loads(original_raw)
    ids,refs,_ = state_after()
    rows = [row for row in original if row['id'] in ids-refs and row['sourceKind'] == 'MAIN' and row['rule'] == 'CompareObjectsWithEquals']
    rows.sort(key=lambda row:row['id'])
    paths = list(dict.fromkeys(row['path'] for row in rows))
    assert len(rows) == 56 and len(paths) == 36 and all(hashes[row['path']] == row['inputSha256'] for row in rows)
    assert all(path.startswith('src/') and '/src/main/java/' in path and path.endswith('.java') and not (data.ROOT/path).is_symlink() for path in paths)
    logical_raw = (data.ROOT/INV).read_bytes(); logical = {row['path']:row for row in json.loads(logical_raw)['artifacts']}
    initial = [dict(path=path,sha256=hashes[path],owner=logical[path]['owner']) for path in paths]
    joined = ownership.join_rows(initial,logical,hashes,'WBS-F03'); ownership.validate(joined,initial,logical,hashes,'WBS-F03')
    assert all(row['canonicalOwner'] and row['canonicalCostOwner'] for row in joined)
    snapshot = Path(normal['jars']['web']['path']).parent.parent.parent.parent
    libraries = []; classpath_files = {}
    for role in ['protocol','storage','bootstrap','api','web','batch']:
        path = snapshot/'src'/('schubert-nk-'+role)/'target/pgpt-test-classpath.txt'
        assert not path.is_symlink(); value = path.read_bytes(); classpath_files[str(path)] = data.sha(value)
        for entry in value.decode().strip().split(os.pathsep):
            candidate = Path(entry)
            if candidate.name.startswith('schubert-nk-') or candidate.is_dir(): continue
            assert candidate.suffix == '.jar' and candidate.is_file() and not candidate.is_symlink() and str(candidate).startswith(str(runner.TC/'m2/repository')+'/')
            libraries.append(str(candidate))
    jars = [value['path'] for value in normal['jars'].values()]
    libraries = list(dict.fromkeys([*jars,*libraries])); dependencies = {path:data.sha(Path(path).read_bytes()) for path in libraries}
    assert all(dependencies[path] == host['begin']['dependencyHashes'][path] for path in jars)
    helper = data.ROOT/'tools/quality/architecture/ThrowableIdentityTypeInspection.java'
    text = helper.read_text()
    assert 'task.parse()' in text and 'task.analyze()' in text and '.generate(' not in text and 'Class.forName' not in text and 'class generation is forbidden' in text
    os.umask(0o077); SLOT.mkdir(); helper_out = SLOT/'helper'; helper_out.mkdir(); empty = SLOT/'empty-processor-path'; empty.mkdir()
    frozen = SLOT/'frozen56.tsv'
    with frozen.open('x') as stream:
        stream.write(''.join('\t'.join([row['id'],row['path'],str(row['line']),row['attributes']['begincolumn']])+'\n' for row in rows))
    begin = dict(source=SOURCE,invocation=invocation,expectedRows=56,expectedSourceFiles=36,
        sourceHashes={path:hashes[path] for path in paths},sourceOwnerRows=joined,
        originalFindingsSha256=data.sha(original_raw),logicalInventorySha256=data.sha(logical_raw),
        originalDiagnostics=rows,frozenRowsSha256=data.sha(frozen.read_bytes()),classpathFiles=classpath_files,
        dependencyHashes=dependencies,helperPath=str(helper),helperSha256=data.sha(helper.read_bytes()),
        javaVersion='25.0.4',os=platform.platform(),python=platform.python_version(),classInitializationOfProductForbidden=True,
        staticOnly=True,productTestsExecuted=0,productCodeChanged=False,newAccepted=0,actualViolationCount=None)
    data.write(SLOT/'begin.safe.json',begin); runner.SLOT = SLOT
    stages = [runner.step('compile-inspector',[str(runner.TC/'jdk-25.0.4/bin/javac'),'--release','25','-proc:none','-Xlint:all','-Werror','-d',str(helper_out),str(helper)],SLOT,timeout=120)]
    if stages[0]['actualExit'] == 0 and not stages[0]['timedOut']:
        compiled = {str(path.relative_to(SLOT)):data.sha(path.read_bytes()) for path in helper_out.rglob('*.class')}
        stages.append(runner.step('inspect-static-types',[str(runner.TC/'jdk-25.0.4/bin/java'),'-Xmx1024m','-Xlog:class+load=info:file='+str(SLOT/'classload-metadata.log'),'-cp',str(helper_out),helper.stem,str(data.ROOT),str(frozen),os.pathsep.join(libraries),str(empty)],SLOT,timeout=240))
    else: compiled = {}
    passed = len(stages) == 2 and all(stage['actualExit'] == 0 and not stage['timedOut'] for stage in stages)
    observed = []; unresolved = []; loaded_product = []
    if len(stages) == 2:
        lines = (SLOT/'inspect-static-types.stdout').read_text().splitlines()
        if passed:
            assert lines[0] == 'DIAGNOSTIC_ERRORS\t0' and lines[1] == 'STATIC_ONLY_NO_GENERATE\ttrue'
            for line in lines[2:]:
                row = line.split('\t')
                if row[0] == 'TYPE':
                    assert len(row) == 12 and row[8] in ['YES','NO','UNKNOWN'] and row[9] in ['YES','NO','UNKNOWN']
                    observed.append(dict(id=row[1],path=row[2],astLine=int(row[3]),astColumn=int(row[4]),operator=row[5],leftType=row[6],rightType=row[7],leftThrowable=row[8],rightThrowable=row[9],enclosingClass=row[10],enclosingMethod=row[11]))
                else:
                    assert row[0] == 'UNRESOLVED' and len(row) == 3; unresolved.append(dict(id=row[1],candidateCount=int(row[2])))
            assert Counter(row['id'] for row in [*observed,*unresolved]) == Counter(row['id'] for row in rows)
        log = (SLOT/'classload-metadata.log').read_text()
        loaded_product = re.findall(r'\[class,load\]\s+(dev\.codex\.schubert\.nk\.\S+)\s+source:',log)
        assert not loaded_product
        assert compiled == {str(path.relative_to(SLOT)):data.sha(path.read_bytes()) for path in helper_out.rglob('*.class')}
    assert not list(empty.iterdir())
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in hashes.items())
    assert all(data.sha(Path(path).read_bytes()) == sha for path,sha in {**dependencies,**classpath_files}.items())
    assert data.sha(helper.read_bytes()) == begin['helperSha256'] and (data.ROOT/INV).read_bytes() == logical_raw
    assert not list(SLOT.rglob('dev/codex/schubert/nk/*.class'))
    verify(invocation); OUT.mkdir()
    records = {row['id']:row for row in rows}; owners = {row['path']:row for row in joined}
    for row in observed:
        original_row = records[row['id']]; assert row['path'] == original_row['path']
        row['sourceSha256'] = hashes[row['path']]; row['canonicalOwner'] = owners[row['path']]['canonicalOwner']; row['canonicalCostOwner'] = owners[row['path']]['canonicalCostOwner']
        row['originalLine'] = original_row['line']; row['originalColumn'] = int(original_row['attributes']['begincolumn'])
        row['sourceSnippet'] = (data.ROOT/row['path']).read_text().splitlines()[original_row['line']-1].strip()
        row['typeEvidence'] = 'BOTH_THROWABLE_REFERENCE_TYPES' if row['leftThrowable'] == row['rightThrowable'] == 'YES' else 'UNRESOLVED_APPLICABILITY'
        row['manualPurposeReviewComplete'] = False
    data.write(OUT/'types.json',dict(source=SOURCE,observed=observed,unresolved=unresolved,productClassesLoaded=loaded_product,sourceOwnerRows=joined))
    value = dict(actualExit=0 if passed else 1,source=SOURCE,begin=begin,stages=stages,observedRows=len(observed),unresolvedRows=len(unresolved),
        bothThrowableTypeCandidates=sum(row['typeEvidence'] == 'BOTH_THROWABLE_REFERENCE_TYPES' for row in observed),
        typesSha256=data.sha((OUT/'types.json').read_bytes()),helperClassHashes=compiled,
        classloadSha256=data.sha((SLOT/'classload-metadata.log').read_bytes()) if (SLOT/'classload-metadata.log').exists() else None,
        productClassesLoaded=0,newProductClassFiles=0,staticOnly=True,productTestsExecuted=0,productCodeChanged=False,
        actualViolationCount=None,newAccepted=0,whole451Accepted=False,wholeF03Accepted=False,effortPercent=None)
    data.write(OUT/'manifest.json',value)
    for name in ['compile-inspector.stdout','compile-inspector.stderr','inspect-static-types.stdout','inspect-static-types.stderr']:
        path = SLOT/name
        if path.exists():
            with (OUT/name).open('xb') as stream: stream.write(path.read_bytes())
    print(json.dumps(dict(actualExit=value['actualExit'],observedRows=len(observed),unresolved=len(unresolved),bothThrowableCandidates=value['bothThrowableTypeCandidates'],manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))
    raise SystemExit(value['actualExit'])

if __name__ == '__main__': main()
