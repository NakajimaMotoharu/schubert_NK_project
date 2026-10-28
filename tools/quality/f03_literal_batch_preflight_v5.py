"""Finite whole-source inverse and original-diagnostic delta; static tools never execute target Tests."""
from collections import Counter
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from f03_literal_batch_sources import original_value, prior_normal, inverse, negative, out
import pg9666_pagination_static as runner

from f03_literal_batch_diagnostic_v3 import signature, selftest
from f03_positioned_ascii_literals import baseline
from f03_all_java_auxiliary import normalize
from pg9978_plain_core_quality_post import test_classes

def preflight(cfg):
    invocation = capture(__file__);format_vectors = selftest();target = out(cfg,cfg.PREFLIGHT_NUMBER)
    slot = data.ROOT.parent/'pgpt-runs/PG379'/target.name.lower();assert not target.exists() and not slot.exists()
    original = original_value(cfg);normal = prior_normal(cfg);hashes = {};inverses = {};negatives = {};expected = {};removed = [];baseline_bindings = {}
    for row in original['sources']:
        path = row['path'];text = (data.ROOT/path).read_text();hashes[path] = data.sha(text.encode())
        inverses[path] = inverse(row['text'],text,row['mapping']);negatives[path] = negative(row['text'],text,row['mapping'])
        selected = {r['id'] for r in row['mapping']};removed += sorted(selected)
        measured,binding = baseline(cfg,row);baseline_bindings[path] = binding
        expected[path] = Counter(signature(r['attributes'],r['message']) for r in measured)
        removal = Counter(signature(r['attributes'],r['message']) for r in row['findings'] if r['id'] in selected)
        assert removal <= expected[path];expected[path].subtract(removal);expected[path] += Counter()
    assert len(removed) == cfg.EXPECTED_CORRECTIONS
    assert {p for p,sha in normal['begin']['inputHashes'].items() if data.sha((data.ROOT/p).read_bytes()) != sha} == set(cfg.PATHS)
    jars = [Path(normal['jars'][r]['path']) for r in ['api','batch','bootstrap','protocol','storage','web']];roots = [p.parent/'test-classes' for p in jars];snapshot = jars[0].parents[3];values = []
    for role in normal['jars']:values.extend((snapshot/('src/schubert-nk-'+role+'/target/pgpt-test-classpath.txt')).read_text().strip().split(os.pathsep))
    auxiliary,externals,replaced,reused = normalize(list(map(str,jars)),list(map(str,roots)),values)
    cp = os.pathsep.join(auxiliary);deps = {str(p):data.sha(p.read_bytes()) for p in [*jars,*map(Path,externals)]}
    classes = test_classes(normal);assert len(classes) == cfg.BASELINE_TEST_PHYSICAL
    class_hashes = {str(Path(normal['jars'][role]['path']).parent/'test-classes'/entry):sha for (role,entry),sha in classes.items()};deps.update(class_hashes)
    static = runner.TC/'static-gates-20261015';rules = data.ROOT/'tools/quality/static'
    pmd = [static/'record-fix-v1/pmd-record-1298.jar',*sorted((static/'pmd-bin-7.28.0/lib').glob('*.jar'))]
    tools = {str(p):data.sha(p.read_bytes()) for p in [*pmd,static/'checkstyle-14.3.0-all.jar',rules/'pmd.xml',rules/'checkstyle.xml',runner.TC/'jdk-25.0.4/bin/java']}
    slot.mkdir();runner.SLOT = slot;listing = slot/'source-list.txt'
    with listing.open('x') as stream:stream.write(''.join(str(data.ROOT/p)+'\n' for p in sorted(hashes)))
    data.write(slot/'begin.safe.json',dict(baseSource=cfg.BASE_SOURCE,invocation=invocation,candidateSourceHashes=hashes,toolAndRuleHashes=tools,dependencyHashes=deps,removedFindingIds=removed,expectedRetainedCounts={path:sum(value.values()) for path,value in expected.items()},originalTokenInverses=inverses,negativeVectors=negatives,auxiliaryClasspath=auxiliary,replacedProjectJars=replaced,freshDuplicateOccurrences=reused,currentMeasuredBaselineBindings=baseline_bindings))
    java = str(runner.TC/'jdk-25.0.4/bin/java')
    stages = {
        'pmd':runner.step('pmd',[java,'-cp',os.pathsep.join(map(str,pmd)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--minimum-priority','5','--aux-classpath',cp,'--no-cache','--format','xml','--report-file',str(slot/'pmd.xml')],slot),
        'checkstyle':runner.step('checkstyle',[java,'-jar',str(static/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(slot/'checkstyle.xml'),'@'+str(listing)],slot),
    }
    actual = {path:Counter() for path in cfg.PATHS};retained = [];root = ET.parse(slot/'pmd.xml').getroot()
    assert not [x for x in root.iter() if x.tag.rpartition('}')[2] in ['error','configerror']]
    for file in root:
        if file.tag.rpartition('}')[2] != 'file':continue
        path = str(Path(file.get('name')).relative_to(data.ROOT));assert path in actual
        for node in file:
            assert node.tag.rpartition('}')[2] == 'violation'
            attrs = dict(node.attrib);message = node.text.strip();actual[path][signature(attrs,message)] += 1
            retained.append(dict(path=path,attributes=attrs,message=message))
    data.write(slot/'observed.safe.json',dict(candidateSourceHashes=hashes,stages=stages,retainedRawFindings=retained,reports={name:data.sha((slot/(name+'.xml')).read_bytes()) for name in stages},diagnosticComparisonMatched=actual==expected))
    assert actual == expected
    assert not [x for x in ET.parse(slot/'checkstyle.xml').getroot().iter() if x.tag == 'error']
    assert stages['pmd']['actualExit'] == (4 if retained else 0) and stages['checkstyle']['actualExit'] == 0 and not any(x['timedOut'] for x in stages.values())
    assert all(data.sha((data.ROOT/path).read_bytes()) == sha for path,sha in hashes.items())
    assert all(data.sha(Path(p).read_bytes()) == sha for p,sha in {**tools,**deps}.items())
    verify(invocation);target.mkdir()
    for name in stages:
        with (target/(name+'.xml')).open('xb') as stream:stream.write((slot/(name+'.xml')).read_bytes())
    data.write(target/'manifest.json',dict(actualExit=0,baseSource=cfg.BASE_SOURCE,source=None,invocation=invocation,candidateSourceHashes=hashes,
        originalTokenInverses=inverses,negativeVectors=negatives,diagnosticFormatVectors=format_vectors,beginSha256=data.sha((slot/'begin.safe.json').read_bytes()),removedFindingIds=removed,retainedRawFindings=retained,
        rawStatic=len(retained),rawStaticGateExit=1 if retained else 0,stages=stages,toolAndRuleHashes=tools,dependencyHashes=deps,
        reports={name:data.sha((target/(name+'.xml')).read_bytes()) for name in stages},
        currentDiagnosticBaselines=baseline_bindings,productTestsExecuted=0,dynamicPtStatus='NOT_EXECUTED_HOLD',coverageStatus='NOT_MEASURED',newAccepted=0,whole451Accepted=False))
    print(data.sha((target/'manifest.json').read_bytes()))
