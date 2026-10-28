"""Two-source oracle projection and unchanged diagnostic multiset, no Test/DB/MVC initialization."""
from collections import Counter
import os
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture,verify
import pg13324_state_oracle_config as cfg
import f03_state_oracle_sources as source
from f03_all_java_auxiliary import normalize
from f03_literal_batch_diagnostic_v3 import signature
from pg9978_plain_core_quality_post import test_classes
import pg9666_pagination_static as runner

OUT = data.BASE/'PG13328-state-oracle-preflight-v1'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg13328-state-oracle-preflight-v1'

def main():
    invocation = capture(__file__);assert not OUT.exists() and not SLOT.exists()
    plan = data.read_checked(data.BASE/'PG13326-state-oracle-plan-v1/manifest.json','ba44fe709ec1593ccefc2f0eb9b0378098e020eacab595a137ea683aa3dcfbfb')
    n = data.read_checked(data.BASE/cfg.OLD_NORMAL[0]/'manifest.json',cfg.OLD_NORMAL[1]);assert plan['source'] == n['source'] == cfg.BASE_SOURCE
    gm = data.read_checked(data.BASE/'PG13253-current-all-java-static-v2/manifest.json','751a5f536623faed78362b14e69da89f5fbdba305acf2b8c1bbbf0811021dbdf')
    global_rows = data.read_checked(data.BASE/'PG13253-current-all-java-static-v2/findings.json',gm['findingsSha256'])
    hashes = {};projections = {};negatives = {};expected = {}
    for path,spec in cfg.SPECS.items():
        text = (data.ROOT/path).read_text();hashes[path] = data.sha(text.encode())
        projections[path] = source.project(source.tokens(text),spec,source.before(path));negatives[path] = source.negatives(text,spec,source.before(path))
        old = [r for r in global_rows if r['path'] == path];assert old and all(r['sourceSha256'] == spec['sha256'] for r in old)
        expected[path] = Counter(signature(r['attributes'],r['message']) for r in old)
    assert {p for p,sha in n['begin']['inputHashes'].items() if data.sha((data.ROOT/p).read_bytes()) != sha} == set(cfg.SPECS)
    jars = [Path(n['jars'][r]['path']) for r in ['api','batch','bootstrap','protocol','storage','web']]
    snapshot = jars[0].parents[3];roots = [p.parent/'test-classes' for p in jars];values = []
    for role in n['jars']:values.extend((snapshot/('src/schubert-nk-'+role+'/target/pgpt-test-classpath.txt')).read_text().strip().split(os.pathsep))
    auxiliary,externals,replaced,reused = normalize(list(map(str,jars)),list(map(str,roots)),values)
    deps = {str(p):data.sha(p.read_bytes()) for p in [*jars,*map(Path,externals)]}
    class_hashes = {str(Path(n['jars'][r]['path']).parent/'test-classes'/entry):sha for (r,entry),sha in test_classes(n).items()};assert len(class_hashes) == 1974
    static = runner.TC/'static-gates-20261015';rules = data.ROOT/'tools/quality/static'
    pmd = [static/'record-fix-v1/pmd-record-1298.jar',*sorted((static/'pmd-bin-7.28.0/lib').glob('*.jar'))]
    tools = {str(p):data.sha(p.read_bytes()) for p in [*pmd,static/'checkstyle-14.3.0-all.jar',rules/'pmd.xml',rules/'checkstyle.xml',runner.TC/'jdk-25.0.4/bin/java']}
    SLOT.mkdir();runner.SLOT = SLOT;listing = SLOT/'source-list.txt'
    with listing.open('x') as f:f.write(''.join(str(data.ROOT/p)+'\n' for p in sorted(hashes)))
    data.write(SLOT/'begin.safe.json',dict(baseSource=cfg.BASE_SOURCE,invocation=invocation,candidateSourceHashes=hashes,sourceProjections=projections,negativeLabels=negatives,
        expectedDiagnosticCounts={p:sum(v.values()) for p,v in expected.items()},toolAndRuleHashes=tools,dependencyHashes=deps,testClassHashes=class_hashes,auxiliaryClasspath=auxiliary,replacedProjectJars=replaced,freshDuplicateOccurrences=reused,productTestsExecuted=0))
    java = str(runner.TC/'jdk-25.0.4/bin/java')
    stages = dict(pmd=runner.step('pmd',[java,'-cp',os.pathsep.join(map(str,pmd)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(rules/'pmd.xml'),'--use-version','java-25','--minimum-priority','5','--aux-classpath',os.pathsep.join(auxiliary),'--no-cache','--format','xml','--report-file',str(SLOT/'pmd.xml')],SLOT),
        checkstyle=runner.step('checkstyle',[java,'-jar',str(static/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(SLOT/'checkstyle.xml'),'@'+str(listing)],SLOT))
    observed = {p:Counter() for p in cfg.SPECS};rows = [];root = ET.parse(SLOT/'pmd.xml').getroot()
    assert not [x for x in root.iter() if x.tag.rpartition('}')[2] in ['error','configerror']]
    for f in root:
        if f.tag.rpartition('}')[2] != 'file':continue
        path = str(Path(f.get('name')).relative_to(data.ROOT));assert path in observed
        for node in f:
            assert node.tag.rpartition('}')[2] == 'violation';attrs = dict(node.attrib);message = ' '.join(''.join(node.itertext()).split())
            observed[path][signature(attrs,message)] += 1;rows.append(dict(path=path,attributes=attrs,message=message))
    reports = {name:data.sha((SLOT/(name+'.xml')).read_bytes()) for name in stages}
    data.write(SLOT/'observed.safe.json',dict(candidateSourceHashes=hashes,stages=stages,reports=reports,findings=rows,diagnosticMultisetUnchanged=observed == expected))
    assert observed == expected and not [x for x in ET.parse(SLOT/'checkstyle.xml').getroot().iter() if x.tag == 'error']
    assert stages['pmd']['actualExit'] == (4 if rows else 0) and stages['checkstyle']['actualExit'] == 0 and not any(r['timedOut'] for r in stages.values())
    assert all(data.sha((data.ROOT/p).read_bytes()) == sha for p,sha in hashes.items()) and all(data.sha(Path(p).read_bytes()) == sha for p,sha in {**tools,**deps,**class_hashes}.items())
    verify(invocation);OUT.mkdir()
    for name in stages:
        with (OUT/(name+'.xml')).open('xb') as f:f.write((SLOT/(name+'.xml')).read_bytes())
    data.write(OUT/'manifest.json',dict(actualExit=0,invocation=invocation,baseSource=cfg.BASE_SOURCE,source=None,candidateSourceHashes=hashes,sourceProjections=projections,negativeLabels=negatives,
        staticMetadataNegativeVectors=sum(len(v) for v in negatives.values()),oracleCallsCorrected=8,newPrivateHelpers=2,newFields=0,diagnosticMultisetUnchanged=True,retainedRawFindings=rows,
        rawStatic=len(rows),rawStaticGateExit=1 if rows else 0,stages=stages,reports=reports,toolAndRuleHashes=tools,dependencyHashes=deps,beginSha256=data.sha((SLOT/'begin.safe.json').read_bytes()),
        productTestsExecuted=0,newAccepted=0,dynamicPtStatus='NOT_EXECUTED_HOLD',coverageStatus='NOT_MEASURED',whole451Accepted=False))
    print(data.sha((OUT/'manifest.json').read_bytes()))

if __name__ == '__main__':main()
