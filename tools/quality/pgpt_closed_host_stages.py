"""Full unchanged static gates and one immutable whole-class run; no automatic retries."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET

import pgpt_closed_host_profile as h


def prepared(c, config):
    p = h.R / c['slots']['prepare'] / 'manifest.json'
    m = h.read_json(p)
    h.require(m['actualExit'] == 0 and m['config'] == h.ref(config) and m['inputHashes'] == h.checked_inputs(c), 'same-input prepared component')
    h.require(m['toolHashes'] == h.tool_hashes(), 'producer/tool source changed after prepare')
    work = h.RUNS / c['privateDirs']['prepare']
    h.require(m['physicalClassHashes'] == h.class_hashes(work / 'component') == h.class_hashes(work / 'target/classes'), 'whole Main physical bytes unchanged')
    h.require(m['testClassHashes'] == h.class_hashes(work / 'test-classes'), 'whole Test bytes unchanged')
    h.require(all(h.digest(Path(p)) == v for p, v in m['dependencies'].items()), 'prepared SDK bytes changed')
    import pgpt_guard_signature
    pgpt_guard_signature.validate_prepared(c, m, work)
    return p, m, work


def findings(path):
    root = ET.parse(path).getroot()
    errors = [dict(x.attrib) for x in root.iter() if x.tag.rpartition('}')[2] in ['error', 'configerror']]
    rows = [dict(path=x.get('name'), rule=y.get('rule'), line=y.get('beginline'), message=(y.text or '').strip()) for x in root if x.tag.rpartition('}')[2] == 'file' for y in x if y.tag.rpartition('}')[2] == 'violation']
    return rows, errors


def static(c, config, extra):
    h.require(not extra, 'static arguments')
    pp, m, work = prepared(c, config)
    out = h.environment(c, 'static')
    paths = c['mainSources'] + [t['path'] for t in c['testSources']]
    listing = out / 'sources.txt'
    listing.write_text(''.join(str(h.R / p) + '\n' for p in paths))
    sg = h.TC / 'static-gates-20261015'
    libs = [sg / 'record-fix-v1/pmd-record-1298.jar', *sorted((sg / 'pmd-bin-7.28.0/lib').glob('*.jar'))]
    compile_only = [m['guardSignature']['compileCarrier']['path']] if m.get('guardSignature') is not None else []
    stages = {'pmd': h.steps.step('pmd', [str(h.JAVA), '-cp', ':'.join(map(str, libs)), 'net.sourceforge.pmd.cli.PmdCli', 'check', '--file-list', str(listing), '--rulesets', str(h.R / 'tools/quality/static/pmd.xml'), '--use-version', 'java-25', '--aux-classpath', str(h.TC / 'jdk-25.0.4/lib/jrt-fs.jar') + ':' + str(work / 'target/classes') + ':' + ':'.join([*m['dependencies'], *compile_only]), '--no-cache', '--format', 'xml', '--report-file', str(out / 'pmd.xml')], h.R)}
    stages['checkstyle'] = h.steps.step('checkstyle', [str(h.JAVA), '-jar', str(sg / 'checkstyle-14.3.0-all.jar'), '-c', str(h.R / 'tools/quality/static/checkstyle.xml'), '-f', 'xml', '-o', str(out / 'checkstyle.xml'), '@' + str(listing)], h.R)
    stages['format'] = h.steps.step('format', [str(h.JAVA), '-jar', str(h.TC / 'google-java-format-1.36.1-all-deps.jar'), '--skip-reflowing-long-strings', '--dry-run', '--set-exit-if-changed', *[str(h.R / p) for p in paths]], h.R)
    stages['spotbugs'] = h.steps.step('spotbugs', [str(h.MAVEN), '-o', '--no-transfer-progress', '-Dmaven.repo.local=' + str(h.TC / 'm2/repository'), '-Dmaven.test.skip=true', 'com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check'], work)
    shutil.copyfile(work / 'target/spotbugsXml.xml', out / 'spotbugs.xml')
    sb = ET.parse(out / 'spotbugs.xml').getroot()
    raw, errors = findings(out / 'pmd.xml')
    m = dict(actualExit=0, config=h.ref(config), prepare=h.ref(pp), inputHashes=m['inputHashes'], stages=stages, rawFindings=raw, processingErrors=errors, checkstyleFindings=len(ET.parse(out / 'checkstyle.xml').findall('.//error')), spotbugs=dict(bugs=len(sb.findall('.//BugInstance')), missing=len(sb.findall('.//MissingClass')), errors=len(sb.findall('.//Error')), classStats=sorted(x.get('class') for x in sb.findall('.//ClassStats'))), fullRootRulesetSha256=h.digest(h.R / 'tools/quality/static/pmd.xml'), productTestsExecuted=0, verifier=h.ref(Path(__file__).resolve()))
    h.write_json(out / 'manifest.json', m)
    return m


def classify_source_findings(paths, anchors, raw, source_text):
    """One identity per actual message when a rule emits several findings at one site."""
    message_mode = any('message' in a for a in anchors)
    expected = set(); classified = []
    fields = {'path', 'rule', 'sourceAnchor', 'occurrences', 'reason', 'disposition'} | ({'message'} if message_mode else set())
    for a in anchors:
        h.require(set(a) == fields and a['disposition'] == 'NOT_APPLICABLE' and isinstance(a['reason'], str) and len(a['reason']) >= 24, 'independent per-site applicability explanation')
        h.require(a['path'] in paths, 'explicit static source scope')
        if message_mode: h.require(isinstance(a['message'], str) and a['message'], 'explicit actual finding message')
        rows = [str(i + 1) for i, line in enumerate(source_text(a['path']).splitlines()) if line.strip() == a['sourceAnchor']]
        h.require(type(a['occurrences']) is int and a['occurrences'] >= 1 and len(rows) == a['occurrences'], 'independent exact source anchor')
        for line in rows:
            identity = (str(h.R / a['path']), a['rule'], line) + ((a['message'],) if message_mode else ())
            h.require(identity not in expected, 'duplicate finding classification')
            expected.add(identity)
            row = dict(path=a['path'], rule=a['rule'], line=line, reason=a['reason'], disposition=a['disposition'])
            if message_mode: row['message'] = a['message']
            classified.append(row)
    actual = [(x['path'], x['rule'], x['line']) + ((x['message'],) if message_mode else ()) for x in raw]
    h.require(len(actual) == len(expected) and set(actual) == expected, 'unclassified/applicable static finding; no blanket Test exemption')
    return classified


def preflight(c, config, extra):
    h.require(len(extra) == 1, 'explicit independent static-admission JSON required')
    admission_path = Path(extra[0]).resolve()
    h.require(admission_path.is_relative_to(h.R / 'evidence') and admission_path.suffix == '.json', 'public static-admission path')
    admission = h.read_json(admission_path)
    h.require(admission.get('schema') == 'PGPT_STATIC_ADMISSION_V1' and admission.get('profile') == c['id'], 'static-admission identity')
    pp, m, work = prepared(c, config)
    sp = h.R / c['slots']['static'] / 'manifest.json'
    st = h.read_json(sp)
    h.require(st['config'] == h.ref(config) and st['prepare'] == h.ref(pp) and st['inputHashes'] == m['inputHashes'], 'same-source static inputs')
    h.require(admission['prepare'] == h.ref(pp) and admission['static'] == h.ref(sp), 'explicit actual static manifest binding')
    h.require(not st['processingErrors'] and not st['checkstyleFindings'] and all(st['spotbugs'][k] == 0 for k in ['bugs', 'missing', 'errors']), 'static errors remain')
    compiler, tag = h.compiler_element()
    h.require(ET.tostring(compiler) == ET.tostring(ET.parse(work / 'pom.xml').getroot().find('.//' + tag('plugin'))) and h.digest(work / 'pom.xml') == m['subsetPomSha256'], 'exact Root compiler configuration')
    classified = classify_source_findings(c['mainSources'] + [x['path'] for x in c['testSources']], admission['sourceAnchors'], st['rawFindings'], lambda p: (h.R / p).read_text())
    h.require({x.replace('.', '/') + '.class' for x in st['spotbugs']['classStats']} == set(m['physicalClassHashes']), 'SpotBugs full physical class universe')
    for p, stages in [(pp, m['stages']), (sp, st['stages'])]:
        for label, v in stages.items():
            h.require(v['actualExit'] == (4 if label == 'pmd' and classified else 0) and not v['timedOut'], 'actual stage exit')
            for stream in ['stdout', 'stderr']:
                h.require(h.digest(p.parent / (label + '.' + stream)) == v[stream + 'Sha256'], 'actual static/compile stream hash')
    out = h.environment(c, 'preflight')
    result = dict(actualExit=0, config=h.ref(config), inputHashes=m['inputHashes'], prepare=h.ref(pp), static=h.ref(sp), staticAdmission=h.ref(admission_path), classified=classified, staticApplicable=0, unclassified=0, processingErrors=0, checkstyle=0, spotbugs=0, rootCompilerUnchanged=True, independentSourceAnchorsExact=True, productTestsExecuted=0, whole451Accepted=False, verifier=h.ref(Path(__file__).resolve()))
    h.write_json(out / 'manifest.json', result)
    return result


def run(c, config, extra):
    h.require(len(extra) == 1 and re.fullmatch(r'[0-9a-f]{40}', extra[0]), 'explicit fixed source')
    source = extra[0]
    h.require(re.fullmatch(r'[0-9a-f]{40}', c.get('productionCoreMain', '')), 'explicit Production Main identity')
    pp, m, work = prepared(c, config)
    pf = h.R / c['slots']['preflight'] / 'manifest.json'
    pre = h.read_json(pf)
    h.require(pre['actualExit'] == 0 and pre['config'] == h.ref(config) and pre['inputHashes'] == m['inputHashes'], 'same-source independent preflight')
    pins = dict(m['inputHashes'])
    pins.update(m['toolHashes'])
    for item in [h.ref(config), pre['staticAdmission'], *c['oracleSpecs'], *c['closureProofs']]:
        pins[item['path']] = item['sha256']
    for name, value in pins.items():
        h.require(hashlib.sha256(subprocess.check_output(['git', 'show', source + ':' + name], cwd=h.R)).hexdigest() == value, 'source not fixed in Git')
    unit = h.RUNS / c['privateDirs']['unit']
    h.require(not unit.exists(), 'one fresh unit run only; recover existing evidence rather than retry')
    out = h.environment(c, 'unit'); unit.mkdir(); (unit / 'tmp').mkdir()
    properties = []
    for key, value in c.get('systemProperties', {}).items():
        properties.append('-D' + key + '=' + (str(work / 'public-repository') if value == 'OWNED_PUBLIC_REPOSITORY' else value))
    agent = h.TC / 'm2/repository/org/jacoco/org.jacoco.agent/0.8.15/org.jacoco.agent-0.8.15-runtime.jar'
    cli = h.TC / 'org.jacoco.cli-0.8.15-nodeps.jar'
    runtime = ':'.join([str(work / 'target/classes'), str(work / 'test-classes'), *m['dependencies']])
    cmd = [str(h.JAVA), '-Djava.io.tmpdir=' + str(unit / 'tmp'), '-Dfile.encoding=UTF-8', '-Duser.timezone=Asia/Tokyo', '-Djunit.jupiter.execution.parallel.enabled=false', '-Djunit.jupiter.extensions.autodetection.enabled=false', *properties, '-javaagent:' + str(agent) + '=destfile=' + str(unit / 'jacoco.exec') + ',sessionid=' + c['id'] + ',append=false', '-Xlog:class+init=info:file=' + str(unit / 'class-init.log'), '-jar', str(h.CONSOLE), 'execute', '--disable-banner', '--class-path', runtime, *[arg for name in m['selectedClasses'] for arg in ['--select-class', name]], '--reports-dir', str(unit / 'xml'), '--fail-if-no-tests', '--details', 'summary']
    begin = dict(source=source, productionCoreMain=c['productionCoreMain'], config=h.ref(config), prepare=h.ref(pp), preflight=h.ref(pf), inputHashes=m['inputHashes'], metadataPins=pins, dependencies=m['dependencies'], physicalClassHashes=m['physicalClassHashes'], testClassHashes=m['testClassHashes'], expectedCases=m['expectedCases'], selectedClasses=m['selectedClasses'], session=c['id'], expectedTests=c['expectedTests'], oldExecUnion=False, coverageExclusions=[], backendOrHeldClassActions=0)
    begin['guardSignature'] = m.get('guardSignature')
    h.write_json(out / 'begin.json', begin)
    stages = {'unit': h.steps.step('unit', cmd, unit)}
    for label, args in [('coverage', ['report', str(unit / 'jacoco.exec'), '--classfiles', str(work / 'component'), '--xml', str(unit / 'coverage.xml')]), ('classinfo', ['classinfo', str(work / 'component')]), ('execinfo', ['execinfo', str(unit / 'jacoco.exec')])]:
        stages[label] = h.steps.step(label, [str(h.JAVA), '-jar', str(cli), *args], h.R)
    cases = []
    for xml in (unit / 'xml').glob('TEST-*.xml'):
        for x in ET.parse(xml).findall('testcase'):
            cases.append(dict(classname=x.get('classname'), name=x.get('name'), failure=x.find('failure') is not None, error=x.find('error') is not None, skipped=x.find('skipped') is not None))
    result = dict(actualExit=stages['unit']['actualExit'], begin=begin, stages=stages, tests=len(cases), cases=cases, failures=sum(x['failure'] for x in cases), errors=sum(x['error'] for x in cases), skipped=sum(x['skipped'] for x in cases), productTestsExecuted=len(cases), formalUpdated=False, whole451Accepted=False)
    h.write_json(out / 'manifest.json', result)
    return result
