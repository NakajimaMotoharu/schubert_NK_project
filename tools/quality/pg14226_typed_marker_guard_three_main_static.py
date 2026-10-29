"""Changed three whole Main only, current Source PMD/Checkstyle; no Product execution."""
from collections import Counter
import json
import os
from pathlib import Path
import platform
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
from pg9906_user_query_oracle_source_post import jar_classes
from pg9978_plain_core_quality_post import test_classes
import pg9666_pagination_static as runner
from f03_all_java_auxiliary import normalize, selftest

SOURCE = '6b53efeec87f3ec36a840dd8e7759656cb4aee5c'
NORMAL = ('PG14216-typed-marker-guard-six-compile-v1','1d0a3dee2f054010a81c67f4a8ef11e7d4370c9640efa9bcb8eead51168c81a3')
OUT = data.BASE/'PG14226-typed-marker-guard-three-main-static-v1'
SLOT = data.ROOT.parent/'pgpt-runs/PG379/pg14226-typed-marker-guard-three-main-static-v1'
ROLES = ['api','batch','bootstrap','protocol','storage','web']

def compact_counts(rows):
    return dict(total=len(rows),byModule=dict(sorted(Counter(r['module'] for r in rows).items())),byKind=dict(sorted(Counter(r['kind'] for r in rows).items())),
        byRule=dict(sorted(Counter(r['rule'] for r in rows).items())),byPath=dict(sorted(Counter(r['path'] for r in rows).items())))

def main():
    invocation = capture(__file__);assert not OUT.exists() and not SLOT.exists()
    n = data.read_checked(data.BASE/NORMAL[0]/'manifest.json',NORMAL[1]);assert n['source'] == SOURCE and n['actualExit'] == n['testsExecuted'] == 0
    snapshots = {Path(item['path']).parents[3] for item in n['jars'].values()};assert len(snapshots) == 1;snapshot = snapshots.pop()
    proof=data.read_checked(data.BASE/'PG14218-typed-marker-guard-source-post-v1/manifest.json','ce3dbfd768a78ef45481db15ecf7c599b00bcb90a5b0b84eac568a54d1dc1909')
    assert proof['source']==SOURCE and proof['actualExit']==0 and len(proof['changedInputPaths'])==3
    sources = {p:sha for p,sha in n['begin']['inputHashes'].items() if p in proof['changedInputPaths']}
    assert len(sources) == 3 and sum('/src/main/java/' in p for p in sources) == 3 and sum('/src/test/java/' in p for p in sources) == 0
    assert all(data.sha((snapshot/p).read_bytes()) == sha == data.sha((data.ROOT/p).read_bytes()) for p,sha in n['begin']['inputHashes'].items())
    assert all(not (snapshot/p).is_symlink() for p in sources)
    main_classes,test_files = jar_classes(n),test_classes(n);assert len(main_classes) == 1843 and len(test_files) == 1978
    assert not {entry for _,entry in main_classes}&{entry for _,entry in test_files}
    duplicate = {}
    for (role,entry),sha in test_files.items():
        if entry in duplicate:assert duplicate[entry] == sha
        else:duplicate[entry] = sha
    fresh_jars = [Path(n['jars'][role]['path']) for role in ROLES]
    test_roots = [path.parent/'test-classes' for path in fresh_jars];assert all(p.is_dir() and p.is_relative_to(snapshot) for p in test_roots)
    dependency_values = []
    scope_vectors = selftest()
    for role in ROLES:
        cp = (snapshot/('src/schubert-nk-'+role+'/target/pgpt-test-classpath.txt')).read_text().strip().split(os.pathsep)
        dependency_values.extend(cp)
    auxiliary,externals,replaced,reused = normalize(list(map(str,fresh_jars)),list(map(str,test_roots)),dependency_values)
    assert all(Path(p).is_file() for p in externals)
    assert not any('/dev/codex/schubert/schubert-nk-' in p for p in auxiliary)
    class_files = {str(Path(n['jars'][role]['path']).parent/'test-classes'/entry):sha for (role,entry),sha in test_files.items()}
    dependencies = {str(p):data.sha(p.read_bytes()) for p in [*fresh_jars,*map(Path,externals)]}
    static = runner.TC/'static-gates-20261015';rules = data.ROOT/'tools/quality/static'
    pmd = [static/'record-fix-v1/pmd-record-1298.jar',*sorted((static/'pmd-bin-7.28.0/lib').glob('*.jar'))]
    tools = {str(p):data.sha(p.read_bytes()) for p in [*pmd,static/'checkstyle-14.3.0-all.jar',rules/'pmd.xml',rules/'checkstyle.xml',runner.TC/'jdk-25.0.4/bin/java']}
    SLOT.mkdir();runner.SLOT = SLOT;listing = SLOT/'source-list.txt'
    with listing.open('x') as stream:stream.write(''.join(str(snapshot/p)+'\n' for p in sorted(sources)))
    begin = dict(source=SOURCE,operatorHead=subprocess.check_output(['git','rev-parse','HEAD'],cwd=data.ROOT,text=True).strip(),branch=subprocess.check_output(['git','branch','--show-current'],cwd=data.ROOT,text=True).strip(),invocation=invocation,normalManifestSha256=NORMAL[1],snapshot=str(snapshot),sourceInputHashes=n['begin']['inputHashes'],
        selectedJavaHashes=sources,mainClassHashes={role+':'+entry:sha for (role,entry),sha in main_classes.items()},testClassFileHashes=class_files,
        dependencyHashes=dependencies,auxiliaryClasspath=auxiliary,replacedOldProjectJars=sorted(replaced),freshProducerOccurrencesDeduplicated=reused,scopeMetadataVectors=scope_vectors,toolAndRuleHashes=tools,
        analysisScope='CHANGED_THREE_MAIN_ONLY_NOT_GLOBAL',sourceCount=3,mainSourceCount=3,testSourceCount=0,mainPhysicalClasses=1843,testPhysicalClasses=1978,
        environment=dict(os=platform.platform(),javaVersion='25.0.4',pmdVersion='7.28.0-with-fixed-record-rule1298',checkstyleVersion='14.3.0'),
        historicalTrackedCatalogReference=8008,actualGlobalWarningCountNotAssumed=True,productTestsExecuted=0,targetAppInvoked=False,externalActions=0)
    data.write(SLOT/'begin.safe.json',begin);java = str(runner.TC/'jdk-25.0.4/bin/java')
    stages = {
        'pmd':runner.step('pmd',[java,'-Xmx4g','-cp',os.pathsep.join(map(str,pmd)),'net.sourceforge.pmd.cli.PmdCli','check','--file-list',str(listing),'--rulesets',str(rules/'pmd.xml'),
            '--use-version','java-25','--minimum-priority','5','--aux-classpath',os.pathsep.join(auxiliary),'--no-cache','--format','xml','--report-file',str(SLOT/'pmd.xml')],SLOT,timeout=900),
        'checkstyle':runner.step('checkstyle',[java,'-Xmx2g','-jar',str(static/'checkstyle-14.3.0-all.jar'),'-c',str(rules/'checkstyle.xml'),'-f','xml','-o',str(SLOT/'checkstyle.xml'),'@'+str(listing)],SLOT,timeout=600),
    }
    rows = [];processing = [];reports = {};seen = {}
    for name in ['pmd','checkstyle']:
        report = SLOT/(name+'.xml');assert report.is_file();root = ET.parse(report).getroot();file_paths = set();count = 0
        for node in root:
            if node.tag.rpartition('}')[2] != 'file':
                if node.tag.rpartition('}')[2] in ['error','configerror']:processing.append(dict(tool=name,attributes=dict(node.attrib),message=' '.join(''.join(node.itertext()).split())))
                continue
            path = str(Path(node.get('name')).relative_to(snapshot));assert path in sources;file_paths.add(path)
            for item in node:
                tag = item.tag.rpartition('}')[2]
                if name == 'pmd' and tag in ['error','configerror']:
                    processing.append(dict(tool=name,path=path,attributes=dict(item.attrib),message=' '.join(''.join(item.itertext()).split())));continue
                assert tag == ('violation' if name == 'pmd' else 'error')
                attrs = dict(item.attrib)
                if name == 'checkstyle' and attrs.get('source') in ['com.puppycrawl.tools.checkstyle.Checker','com.puppycrawl.tools.checkstyle.TreeWalker']:
                    processing.append(dict(tool=name,path=path,attributes=attrs,message=attrs.get('message','')))
                role = path.split('/')[1].removeprefix('schubert-nk-');kind = 'main' if '/src/main/java/' in path else 'test'
                row = dict(tool=name,path=path,sourceSha256=sources[path],module=role,kind=kind,attributes=attrs,
                    rule=attrs.get('rule',attrs.get('source','UNKNOWN')),message=' '.join(''.join(item.itertext()).split()) if name == 'pmd' else attrs.get('message',''))
                assert role in ROLES;rows.append(row);count += 1
        seen[name] = sorted(file_paths);reports[name] = dict(sha256=data.sha(report.read_bytes()),findings=count,filesInReport=len(file_paths),actualExit=stages[name]['actualExit'])
    assert set(seen['checkstyle']) == set(sources)
    assert all(data.sha((snapshot/p).read_bytes()) == sha == data.sha((data.ROOT/p).read_bytes()) for p,sha in n['begin']['inputHashes'].items())
    assert all(data.sha(Path(p).read_bytes()) == sha for p,sha in {**class_files,**dependencies,**tools}.items())
    assert jar_classes(n) == main_classes and test_classes(n) == test_files
    complete = not processing and stages['pmd']['actualExit'] in [0,4] and not any(row['timedOut'] for row in stages.values())
    # The CS exit is preserved verbatim; raw warnings determine quality, not an exit-code normalization.
    complete = complete and (stages['checkstyle']['actualExit'] == 0 or reports['checkstyle']['findings'] > 0)
    verify(invocation);OUT.mkdir()
    for name in reports:
        with (OUT/(name+'.xml')).open('xb') as stream:stream.write((SLOT/(name+'.xml')).read_bytes())
    data.write(OUT/'findings.json',rows)
    data.write(OUT/'manifest.json',dict(actualExit=0 if complete else 1,source=SOURCE,invocation=invocation,beginSha256=data.sha((SLOT/'begin.safe.json').read_bytes()),normalManifestSha256=NORMAL[1],stages=stages,reports=reports,
        findingsSha256=data.sha((OUT/'findings.json').read_bytes()),counts={name:compact_counts([r for r in rows if r['tool'] == name]) for name in reports},processingErrors=processing,
        analysisScope='CHANGED_THREE_MAIN_ONLY_NOT_GLOBAL',sourceCount=3,mainSourceCount=3,testSourceCount=0,mainPhysicalClasses=1843,testPhysicalClasses=1978,allInputHashesUnchanged=True,
        analysisComplete=complete,qualityGateExit=0 if complete and not rows else 1,historicalTrackedCatalogReference=8008,rawCountsAreNotViolationOrEffortCounts=True,
        actualFileOwnerCosts=None,productTestsExecuted=0,targetAppInvoked=False,externalActions=0,newAccepted=0,wholeF03Accepted=False,whole451Accepted=False,effortPercent=None))
    print(json.dumps(dict(actualExit=0 if complete else 1,qualityGateExit=0 if complete and not rows else 1,counts={k:v['findings'] for k,v in reports.items()},processingErrors=len(processing),manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))),flush=True)
    raise SystemExit(0 if complete else 1)

if __name__ == '__main__':main()
