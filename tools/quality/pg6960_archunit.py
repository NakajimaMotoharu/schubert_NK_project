"""F02 SS311 bytecode architecture qualification on returned original Jars only.

Own javac canaries + ArchUnit static importer are not new Production PT/native.
Every child exit is persisted before semantic validation; existing unfinished steps
are never started again. Runtime libraries, source/POMs and original jobs are untouched.
"""
import datetime
import hashlib
import json
import os
import subprocess
import zipfile
from pathlib import Path

from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6932_original4222_artifacts import read_whole

TC = ROOT.parent / 'toolchain'
JAVA = TC / 'jdk-25.0.4/bin/java'
JAVAC = JAVA.with_name('javac')
ARCH = TC / 'architecture/archunit-1.4.2/archunit-1.4.2.jar'
ARCH_SHA = '6d8adf69a3f109ebe1b395764feb07f919e9e0e2ab5e2ea141d2e6251ba7d17f'
SLF = TC / 'm2/repository/org/slf4j/slf4j-api/2.0.18/slf4j-api-2.0.18.jar'
SLF_SHA = '44508fd1576500688c790b190acdd16fec4f8c79a3e0b900afd70503cf055f55'
MODULES = ('protocol', 'storage', 'bootstrap', 'api', 'web', 'batch')
RULES = {'MODULE_EDGES', 'FRAMEWORK_FENCES', 'CONTROLLER_BOUNDARY', 'REPOSITORY_DIRECTION', 'INTERNAL_OWNER'}
SLOT = W / 'pg6960-archunit-static-v1'
OUT = BASE / 'PG6960-archunit-static-v1'
SOURCE = ROOT / 'tools/quality/architecture/ModuleDependencyAudit.java'
P = 'dev.codex.schubert.nk.'
BASE_CLASSES = {
 P+'protocol.Probe': 'package '+P+'protocol; public final class Probe { static { System.setProperty("nk.archunit.canary.initialized","true"); } }',
 P+'storage.Value': 'package '+P+'storage; public final class Value {}',
 P+'api.bootstrap.Alias': 'package '+P+'api.bootstrap; public final class Alias { public '+P+'storage.Value value; }',
 P+'api.Probe': 'package '+P+'api; public final class Probe { public '+P+'api.bootstrap.Alias value; }',
 P+'web.Probe': 'package '+P+'web; public final class Probe { public '+P+'api.bootstrap.Alias value; }',
 P+'batch.Probe': 'package '+P+'batch; public final class Probe { public '+P+'api.bootstrap.Alias value; }',
 P+'api.application.High': 'package '+P+'api.application; public final class High { public static void run() {} }',
}
EXTRA_CLASSES = {
 P+'protocol.BadJdbc': 'package '+P+'protocol; public final class BadJdbc { public java.sql.Connection value; }',
 P+'storage.BadJdbc': 'package '+P+'storage; public final class BadJdbc { public java.sql.Connection value; }',
 P+'api.bootstrap.BadHttp': 'package '+P+'api.bootstrap; public final class BadHttp { public com.sun.net.httpserver.HttpServer value; }',
 P+'api.BadWeb': 'package '+P+'api; public final class BadWeb { public '+P+'web.Probe value; }',
 P+'web.BadApi': 'package '+P+'web; public final class BadApi { public '+P+'api.Probe value; }',
 P+'batch.BadHttp': 'package '+P+'batch; public final class BadHttp { public com.sun.net.httpserver.HttpServer value; }',
 P+'web.session.BadController': 'package '+P+'web.session; public final class BadController { public java.sql.Connection value; }',
 P+'api.persistence.BadRepo': 'package '+P+'api.persistence; public final class BadRepo { public void run() { '+P+'api.application.High.run(); } }',
 'org.springframework.web.servlet.ModelAndView': 'package org.springframework.web.servlet; public final class ModelAndView {}',
 P+'api.BadMvc': 'package '+P+'api; public final class BadMvc { public org.springframework.web.servlet.ModelAndView value; }',
 P+'api.missing.Marker': 'package '+P+'api.missing; public final class Marker {}',
 P+'web.BadUnknown': 'package '+P+'web; public final class BadUnknown { public '+P+'api.missing.Marker value; }',
}


def require(value, label):
    if not value:
        raise ValueError(label)


def dump_new(path, value):
    with path.open('x') as stream:
        json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def step(name, command):
    begin = SLOT / (name + '.begin.safe.json')
    end = SLOT / (name + '.exit.safe.json')
    if end.exists():
        value = json.loads(end.read_bytes())
        require(value['command'] == command and sha(SLOT / value['stdout']) == value['stdoutSha256']
                and sha(SLOT / value['stderr']) == value['stderrSha256'], 'fixed original completed step only')
        return value, (SLOT / value['stdout']).read_text()
    require(not begin.exists(), 'unfinished original step: preserve/observe, never restart')
    value = dict(command=command, startUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 stdout=name + '.stdout.safe.log', stderr=name + '.stderr.safe.log',
                 programSha256=sha(SOURCE), driverSha256=sha(Path(__file__)))
    dump_new(begin, value)
    env = {'PATH':'/usr/bin:/bin', 'LANG':'C.UTF-8', 'JAVA_HOME':str(JAVA.parents[1])}
    with (SLOT / value['stdout']).open('xb') as stdout, (SLOT / value['stderr']).open('xb') as stderr:
        process = subprocess.run(command, cwd=SLOT, env=env, stdout=stdout, stderr=stderr, timeout=120)
    value.update(actualExit=process.returncode, endUTC=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 stdoutSha256=sha(SLOT / value['stdout']), stderrSha256=sha(SLOT / value['stderr']))
    dump_new(end, value)  # Before compile/result/canary interpretation.
    return value, (SLOT / value['stdout']).read_text()


def parse(text):
    result = dict(rules={}, modules={}, findings=[])
    for line in text.splitlines():
        cells = line.split('\t')
        if cells[0] == 'ARCHUNIT' and len(cells) == 4 and 'version' not in result:
            result.update(version=cells[1], physical=int(cells[2]), imported=int(cells[3]))
        elif cells[0] == 'MODULE' and len(cells) == 3 and cells[1] not in result['modules']:
            result['modules'][cells[1]] = int(cells[2])
        elif cells[0] == 'RULE' and len(cells) == 3 and cells[1] not in result['rules']:
            result['rules'][cells[1]] = int(cells[2])
        elif cells[0] == 'FINDING' and len(cells) == 4:
            result['findings'].append(dict(rule=cells[1], origin=cells[2], target=cells[3]))
        elif cells[0] == 'INSPECTED' and len(cells) == 3 and 'dependencies' not in result:
            result.update(dependencies=int(cells[1]), calls=int(cells[2]))
        else:
            raise ValueError('complete fixed diagnostic grammar, no dropped rows')
    require(result.get('version') == '1.4.2' and set(result['modules']) == set(MODULES)
            and set(result['rules']) == RULES and result['physical'] == result['imported'] > 0
            and sum(result['modules'].values()) == result['physical']
            and all(v > 0 for v in result['modules'].values()) and result.get('dependencies', 0) > 0
            and sum(result['rules'].values()) == len(result['findings']), 'nonvacuous full inventory/rule result')
    require(all(sum(f['rule'] == r for f in result['findings']) == n for r, n in result['rules'].items()),
            'all rule failures accounted')
    return result


def fixtures():
    sources = SLOT / 'canary-source'
    target = SLOT / 'canary-classes'
    sources.mkdir(exist_ok=True)
    target.mkdir(exist_ok=True)
    paths = []
    for name, text in {**BASE_CLASSES, **EXTRA_CLASSES}.items():
        path = sources / (name.replace('.', '/') + '.java')
        path.parent.mkdir(parents=True, exist_ok=True)
        data = (text + '\n').encode()
        if path.exists():
            require(path.read_bytes() == data, 'canary source fixed')
        else:
            with path.open('xb') as stream:
                stream.write(data)
        paths.append(path)
    receipt, _ = step('002-canary-compile', [str(JAVAC), '--release','25','-proc:none','-Xlint:all','-Werror',
                                             '-d',str(target), *[str(p) for p in paths]])
    require(receipt['actualExit'] == 0, 'own independent canary compile')
    baseline = {m:[] for m in MODULES}
    for name in BASE_CLASSES:
        module = 'bootstrap' if name == P+'api.bootstrap.Alias' else name[len(P):].split('.')[0]
        baseline[module].append(name)
    variants = [('positive', {}, set())]
    for label, module, names, rules in (
      ('protocol-jdbc','protocol',[P+'protocol.BadJdbc'],{'FRAMEWORK_FENCES'}),
      ('storage-jdbc','storage',[P+'storage.BadJdbc'],{'FRAMEWORK_FENCES'}),
      ('bootstrap-http','bootstrap',[P+'api.bootstrap.BadHttp'],{'FRAMEWORK_FENCES'}),
      ('api-web','api',[P+'api.BadWeb'],{'MODULE_EDGES'}),
      ('web-api','web',[P+'web.BadApi'],{'MODULE_EDGES'}),
      ('batch-http','batch',[P+'batch.BadHttp'],{'FRAMEWORK_FENCES'}),
      ('controller-jdbc','web',[P+'web.session.BadController'],{'CONTROLLER_BOUNDARY'}),
      ('repository-upcall','api',[P+'api.persistence.BadRepo'],{'REPOSITORY_DIRECTION'}),
      ('api-mvc','api',[P+'api.BadMvc','org.springframework.web.servlet.ModelAndView'],{'FRAMEWORK_FENCES'}),
      ('unknown-owner','web',[P+'web.BadUnknown'],{'INTERNAL_OWNER'})):
        variants.append((label, {module:names}, rules))
    result = []
    for label, additions, expected_rules in variants:
        folder = SLOT / ('canary-' + label)
        folder.mkdir(exist_ok=True)
        jars = {}
        for module in MODULES:
            path = folder / (module + '.jar')
            names = sorted(baseline[module] + additions.get(module, []))
            expected = {n.replace('.', '/')+'.class':(target / (n.replace('.', '/')+'.class')).read_bytes() for n in names}
            if path.exists():
                with zipfile.ZipFile(path) as jar:
                    require({n:jar.read(n) for n in jar.namelist()} == expected, 'own fixed original canary Jar')
            else:
                with zipfile.ZipFile(path, 'x') as jar:
                    for n, data in expected.items():
                        jar.writestr(n, data)
            jars[module] = path
        result.append((label, jars, expected_rules))
    return result


def evaluate(name, jars):
    cp = os.pathsep.join([str(SLOT / 'tool-classes'), str(ARCH), str(SLF)])
    receipt, text = step(name, [str(JAVA), '-cp',cp, 'ModuleDependencyAudit',
                               *[m+'='+str(jars[m]) for m in MODULES]])
    parsed = parse(text)
    require(receipt['actualExit'] == (1 if parsed['findings'] else 0), 'true process exit matches diagnostics')
    return dict(receipt=receipt, result=parsed)


def main():
    require(sha(ARCH) == ARCH_SHA and sha(SLF) == SLF_SHA, 'fixed tool-only library bytes')
    qp, q, _ = read_whole()
    require(sha(qp) == '728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731', 'fixed whole proof')
    original = W / 'pg6932-original4222-artifacts-v1/jars'
    jars = {m:original / ('schubert-nk-'+m+'.jar') for m in MODULES}
    physical = {}
    for module, path in jars.items():
        with zipfile.ZipFile(path) as jar:
            for name in jar.namelist():
                if name.endswith('.class'):
                    require(module+':'+name not in physical, 'unique physical class')
                    physical[module+':'+name] = hashlib.sha256(jar.read(name)).hexdigest()
    require(physical == q['allPhysicalMainSha256'] and len(physical) == 1669, 'all original1669 physical classes, no native transfer')
    SLOT.mkdir(mode=0o700, exist_ok=True)
    classes = SLOT / 'tool-classes'
    classes.mkdir(exist_ok=True)
    compile_receipt, _ = step('001-tool-compile', [str(JAVAC), '--release','25','-proc:none','-Xlint:all','-Werror',
                                                '-cp',os.pathsep.join([str(ARCH),str(SLF)]), '-d',str(classes),str(SOURCE)])
    require(compile_receipt['actualExit'] == 0, 'static helper compile')
    canaries = []
    for index, (name, paths, expected_rules) in enumerate(fixtures(), 3):
        result = evaluate(f'{index:03}-canary-'+name, paths)
        failed = {k for k, v in result['result']['rules'].items() if v}
        require(failed == expected_rules, 'independent positive/negative rule identity, no adjusted expectation')
        canaries.append(dict(name=name, expectedViolatedRules=sorted(expected_rules), **result))
    actual = evaluate('014-original-six', jars)
    value = dict(actualExit=actual['receipt']['actualExit'], source=q['productionSource'], run='PG6930-six-v1',
                 originalQualificationSha256=sha(qp), physicalClasses=1669,
                 originalJarHashes={m:sha(p) for m,p in jars.items()},
                 staticResult=actual, canaries=canaries, compileReceipt=compile_receipt,
                 archunitVersion='1.4.2', archunitSha256=ARCH_SHA, slf4jVersion='2.0.18', slf4jSha256=SLF_SHA,
                 javaBinarySha256=sha(JAVA), javacBinarySha256=sha(JAVAC),
                 toolSourceSha256=sha(SOURCE), driverSha256=sha(Path(__file__)),
                 targetClassesInitialized=False, F03Accepted=False, formalAccepted=False,
                 testsExecuted=0, originalWholeReplayed=False, vmActions=0,
                 productionMainTestPomChanges=0, interpretation='ADDITIONAL_ARCHITECTURE_STATIC_CHECK_NOT_PT_PASS_OR_COVERAGE',
                 completedUTC=datetime.datetime.now(datetime.timezone.utc).isoformat())
    OUT.mkdir()
    path = OUT / 'manifest.json'
    dump_new(path, value)
    print(json.dumps(dict(actualExit=value['actualExit'], manifestSha256=sha(path),
                         originalFindings=len(actual['result']['findings']), canaries=len(canaries), physicalClasses=1669)))
    return value['actualExit']


if __name__ == '__main__':
    raise SystemExit(main())
