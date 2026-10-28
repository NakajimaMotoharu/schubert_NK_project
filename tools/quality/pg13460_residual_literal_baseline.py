"""Collect current diagnostics for70 residual-literal sources; never execute a target Test."""
from collections import Counter
import json
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg13458_residual_literal_plan as plan
from f03_all_java_auxiliary import normalize
from f03_literal_batch_diagnostic_v3 import signature
from pg9978_plain_core_quality_post import test_classes
import pg9666_pagination_static as runner

OUT = data.BASE/'PG13460-residual-literal-current-baseline-v1'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13460-residual-literal-current-baseline-v1'


def main():
    invocation = capture(__file__)
    assert not SLOT.exists() and not OUT.exists()
    normal = data.read_checked(data.BASE/plan.NORMAL[0]/'manifest.json',plan.NORMAL[1])
    assert normal['source'] == plan.SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    source_hashes = normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in source_hashes.items())
    assert all(source_hashes[path] == sha for path,sha in plan.BASELINE_PATHS.items())
    jars = [Path(normal['jars'][role]['path']) for role in ['api','batch','bootstrap','protocol','storage','web']]
    snapshot = jars[0].parents[3]
    roots = [path.parent/'test-classes' for path in jars]
    assert all(data.sha((snapshot/path).read_bytes()) == sha for path,sha in source_hashes.items())
    values = []
    for role in normal['jars']:
        values.extend((snapshot/('src/schubert-nk-'+role+'/target/pgpt-test-classpath.txt')).read_text().strip().split(os.pathsep))
    auxiliary,external,replaced,reused = normalize(list(map(str,jars)),list(map(str,roots)),values)
    dependencies = {str(path):data.sha(path.read_bytes()) for path in [*jars,*map(Path,external)]}
    classes = test_classes(normal)
    assert len(classes) == 1978
    dependencies.update({str(Path(normal['jars'][role]['path']).parent/'test-classes'/entry):sha for (role,entry),sha in classes.items()})
    static = runner.TC/'static-gates-20261015'
    rules = data.ROOT/'tools/quality/static'
    pmd = [static/'record-fix-v1/pmd-record-1298.jar',*sorted((static/'pmd-bin-7.28.0/lib').glob('*.jar'))]
    tool_hashes = {str(path):data.sha(path.read_bytes()) for path in [*pmd,static/'checkstyle-14.3.0-all.jar',rules/'pmd.xml',rules/'checkstyle.xml',runner.TC/'jdk-25.0.4/bin/java']}
    SLOT.mkdir()
    runner.SLOT = SLOT
    listing = SLOT/'sources.txt'
    with listing.open('x') as stream:
        stream.write(''.join(str(data.ROOT/path)+'\n' for path in sorted(plan.BASELINE_PATHS)))
    data.write(SLOT/'begin.safe.json',dict(source=plan.SOURCE,invocation=invocation,normalManifestSha256=plan.NORMAL[1],candidateSourceHashes=plan.BASELINE_PATHS,
        toolAndRuleHashes=tool_hashes,dependencyHashes=dependencies,auxiliaryClasspath=auxiliary,replacedProjectJars=replaced,freshDuplicateOccurrences=reused,
        originalResidualIds=plan.ORIGINAL_RESIDUAL_IDS,productTestsExecuted=0,externalActions=0))
    java = str(runner.TC/'jdk-25.0.4/bin/java')
    stages = {
        'pmd':runner.step('pmd',[java,'-cp',os.pathsep.join(map(str,pmd)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--minimum-priority','5','--aux-classpath',os.pathsep.join(auxiliary),'--no-cache','--format','xml','--report-file',str(SLOT/'pmd.xml')],SLOT),
        'checkstyle':runner.step('checkstyle',[java,'-jar',str(static/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(SLOT/'checkstyle.xml'),'@'+str(listing)],SLOT),
    }
    pmd_root = ET.parse(SLOT/'pmd.xml').getroot()
    processing = [node.tag for node in pmd_root.iter() if node.tag.rpartition('}')[2] in ['error','configerror']]
    rows = []
    for file in pmd_root:
        if file.tag.rpartition('}')[2] != 'file':
            continue
        path = str(Path(file.get('name')).relative_to(data.ROOT))
        assert path in plan.BASELINE_PATHS
        for node in file:
            assert node.tag.rpartition('}')[2] == 'violation'
            rows.append(dict(path=path,attributes=dict(node.attrib),message=node.text.strip()))
    cs_errors = len(list(ET.parse(SLOT/'checkstyle.xml').getroot().iter('error')))
    complete = not processing and cs_errors == 0 and stages['pmd']['actualExit'] == (4 if rows else 0) and stages['checkstyle']['actualExit'] == 0 and not any(stage['timedOut'] for stage in stages.values())
    original_raw = (data.BASE/'PG10690-current-global-static-post-v1/findings.json').read_bytes()
    selected_ids = set(plan.ORIGINAL_RESIDUAL_IDS)
    original = [row for row in json.loads(original_raw) if row['id'] in selected_ids]
    assert len(original) == len(plan.ORIGINAL_RESIDUAL_IDS) == 251
    available = Counter((row['path'],signature(row['attributes'],row['message'])) for row in rows)
    matched,missing = [],[]
    for row in sorted(original,key=lambda r:r['id']):
        key = row['path'],signature(row['attributes'],row['message'])
        if available[key]:
            matched.append(row['id'])
            available[key] -= 1
        else:
            missing.append(row['id'])
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in source_hashes.items())
    assert all(data.sha(Path(path).read_bytes()) == sha for path,sha in {**dependencies,**tool_hashes}.items())
    verify(invocation)
    OUT.mkdir()
    reports = {}
    for label in stages:
        raw = (SLOT/(label+'.xml')).read_bytes()
        with (OUT/(label+'.xml')).open('xb') as stream:
            stream.write(raw)
        reports[label] = data.sha(raw)
    data.write(OUT/'manifest.json',dict(actualExit=0 if complete else 1,collectionComplete=complete,source=plan.SOURCE,invocation=invocation,normalManifestSha256=plan.NORMAL[1],
        beginSha256=data.sha((SLOT/'begin.safe.json').read_bytes()),candidateSourceHashes=plan.BASELINE_PATHS,retainedRawFindings=rows,rawStatic=len(rows),rawStaticGateExit=1 if rows or cs_errors else 0,
        collectionExitIsNotQualityPass=True,processingErrors=processing,checkstyleErrors=cs_errors,stages=stages,reports=reports,dependencyHashes=dependencies,toolAndRuleHashes=tool_hashes,
        originalResidualIds=plan.ORIGINAL_RESIDUAL_IDS,observedOriginalResidualIds=matched,missingOriginalResidualIds=missing,originalFindingsSha256=data.sha(original_raw),
        currentDuplicateLiteralRows=sum(row['attributes']['rule']=='AvoidDuplicateLiterals' for row in rows),sourceChanged=False,newAccepted=0,productTestsExecuted=0,newTestIds=0,
        coverage=None,formalUpdated=False,whole451Accepted=False,wholeF03Accepted=False,unknownOwnersNotAssigned=True,externalActions=0))
    print(dict(collectionExit=0 if complete else 1,rawStatic=len(rows),rawQualityGateExit=1 if rows or cs_errors else 0,originalResidualMatched=len(matched),originalResidualMissing=len(missing),manifestSha256=data.sha((OUT/'manifest.json').read_bytes())))
    raise SystemExit(0 if complete else 1)


if __name__ == '__main__':
    main()
