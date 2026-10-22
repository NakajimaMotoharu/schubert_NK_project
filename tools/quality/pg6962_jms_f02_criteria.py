"""JMS three components + F02 criterion witness from genuine completed4222.

No build/PT/VM/service replay. The only new executions are version queries and
disassembly of five original abstract interfaces; ArchUnit has its own receipt.
"""
import argparse
import copy
import hashlib
import json
import os
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import pg6958_recovery_catalog as initial
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6932_original4222_artifacts import read_whole
import wbs_progress_audit as audit

SOURCE = initial.SOURCE
PMO = initial.PMO
IDS = ('WBS-P005-02', 'WBS-P005-03', 'WBS-P005-04', 'WBS-F02')
PRIOR = PMO / '488_当source個別受入_必要四依存・catalog.json'
REVIEW = 'evidence/01_PT/018_NK-OPS-001/1526_リカバリJMS三領域・F02個別PG品質matrix.md'
OUT = BASE / 'PG6962-jms-f02-criteria-v1'
EXTRA = {
 'WBS-P005-02': tuple('web:messaging.' + n for n in (
   'BrokerGraph334Test','ExceptionValueContractTest','ReplyCleanup333Test',
   'ReplyCommittedTerminalAdmissionContractTest','ReplyConsumerGraph332Test',
   'ReplyFatalIsolationContractTest','ReplyIsolationPrimaryContractTest','ReplyRollbackSignalContractTest',
   'ReplyRollbackUnconfirmedContractTest','WebBrokerFactoryOwnershipTest','WebFactoryNativeRetentionTest',
   'WebBusinessWireClientsTest','ScenarioWireClientTest','AnimationWireClientTest','MusicWireClientTest'))
   + ('protocol:codec.FieldCodecTest','protocol:codec.MessageCodecTest','protocol:codec.PayloadCodecTest',
      'protocol:codec.PayloadGoldenVectorTest','protocol:time.JstWireTimestampTest'),
 'WBS-P005-03': tuple('api:messaging.inbound.' + n for n in (
   'ApiConsumerCloseOwnershipTest','ApiConsumerRemainderTest','ApiConsumerTerminalRemainderTest',
   'ApiNativeRetentionTest','CommittedTerminalAdmissionContractTest','ConfirmedRollbackCallbackTest',
   'ConsumerCleanup333Test','ConsumerGraph332Test','ConsumerRollbackUnconfirmedContractTest',
   'FatalIsolationConsumersContractTest','InboundTransactionsPrimaryContractTest','InternalEventListenerTest',
   'ParentGraph334Test','WebLogConsumersTest','QuestionWorkConsumersTest'))
   + tuple('api:messaging.config.' + n for n in (
     'ApiFactoryOwnershipTest','ApiBrokerFactoryRemainderTest','ApiFactoryNativeRetentionTest','BrokerGraph334Test'))
   + ('api:messaging.outbound.OutboundJmsAdapterTest','api:messaging.outbound.OutboxDlqMetadataTest',
      'protocol:transport.FailedJmsIsolationExceptionTest','protocol:transport.UnconfirmedJmsRollbackExceptionTest'),
 'WBS-P005-04': tuple('api:messaging.config.' + n for n in (
   'ApiBrokerContextsTest','ApiFactoryOwnershipTest','ApiBrokerFactoryRemainderTest',
   'ApiFactoryNativeRetentionTest','BrokerGraph334Test')) + ('api:messaging.outbound.OutboundJmsAdapterTest',),
 'WBS-F02': ('batch:bootstrap.BatchRuntimeDependencyTest','web:bootstrap.WebRuntimeDependencyTest'),
}
NS = {'m':'http://maven.apache.org/POM/4.0.0'}
ALLOWED = {'protocol':set(),'storage':set(),'bootstrap':{'storage'},
           'api':{'protocol','storage','bootstrap'},'web':{'protocol','storage','bootstrap'},'batch':{'storage','bootstrap'}}
MANAGED = {('commons-logging','commons-logging'):'1.4.0', ('org.jspecify','jspecify'):'1.0.1', ('org.slf4j','slf4j-api'):'2.0.18'}
INTERFACES = {
 'web:dev/codex/schubert/nk/web/messaging/JmsContextFactory.class',
 'web:dev/codex/schubert/nk/web/messaging/JmsRequestSender.class',
 'api:dev/codex/schubert/nk/api/messaging/inbound/SyncRequestProcessor.class',
 'api:dev/codex/schubert/nk/api/messaging/outbound/SqlConnectionProvider.class',
 'api:dev/codex/schubert/nk/api/messaging/outbound/TransactedJmsContextProvider.class'}
SUPPORT = {
 'src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/transport/FailedJmsIsolationException.java':
  ('8b22ea28c7a14624bb86b6a8b80661460d446418b61b76c42cdbba7f7f74dfbb','6b5cea563b6f68b0b604afc06490063793e49662'),
 'src/schubert-nk-protocol/src/main/java/dev/codex/schubert/nk/protocol/transport/UnconfirmedJmsRollbackException.java':
  ('4ca8f9a3d350557e66b026eb96753c6cac7fe14c3204fc302af86f0dd2795938','226fbb6c5348ae0ade9d25f8c579c43d653298a9')}


def require(value, message):
    if not value:
        raise ValueError(message)


def selector(path):
    module = path.split('/')[1].removeprefix('schubert-nk-')
    return module + ':' + path.split('/src/test/java/dev/codex/schubert/nk/' + module + '/')[1][:-5].replace('/', '.')


def scope_rows(task, artifacts, inputs):
    selected = [a for a in artifacts if a['owner'] == task['id']]
    logical = {a['path']:a['sha256'] for a in selected if not a.get('implementationSupportOnly',False)}
    support = {a['path']:a for a in selected if a.get('implementationSupportOnly',False)}
    require(len(selected) == len(logical) + len(support) and set(logical) == set(task['ownedArtifacts']),
            'exact logical scope, no duplicate/missing/unregistered extra')
    expected = SUPPORT if task['id'] == 'WBS-P005-03' else {}
    require(set(support) == set(expected),'both existing support artifacts only at declared owner')
    for path, row in support.items():
        digest, origin = expected[path]
        require(row['owner'] == row['costOwner'] == row['supportingExistingLeaf'] == 'WBS-P005-03'
                and row['implementationSupportOnly'] is True and row['additionalBudgetPp'] == 0
                and row['historicalPath'] is None and row['kind'] == 'JAVA' and row['module'] == 'protocol'
                and row['class'] == path.split('/src/main/java/')[1][:-5]
                and row['originCommit'] == origin and row['sha256'] == digest == inputs[path],
                'full registered support identity/source/provenance/cost-zero contract')
    require(all(inputs[p] == h for p,h in logical.items()),'all logical artifact original bytes')
    return logical, [support[p] for p in sorted(support)]


def family(path, q):
    if path.endswith('/package-info.java'):
        return dict(applicability='PACKAGE_ANNOTATION_NO_EXECUTABLE_METHOD', counters={})
    module = path.split('/')[1].removeprefix('schubert-nk-')
    name = path.split('/src/main/java/')[1][:-5]
    rows = {k:v for k,v in q['allActualClassCounters'].items()
            if k == module+':'+name+'.class' or k.startswith(module+':'+name+'$')}
    require(rows, 'every executable or abstract physical family present')
    declarations = {}
    for key, counter in rows.items():
        if counter:
            require(all(k in initial.TYPES and v['missed'] == 0 for k,v in counter.items())
                    and all(counter[k]['covered'] > 0 for k in ('LINE','METHOD','CLASS')), 'real family allmiss0/positive')
            continue
        require(key in INTERFACES, 'only five explicitly declared empty interfaces, no unknown skip')
        member = key.split(':',1)[1]
        jar = W / ('pg6932-original4222-artifacts-v1/jars/schubert-nk-'+module+'.jar')
        with zipfile.ZipFile(jar) as zipped:
            digest = hashlib.sha256(zipped.read(member)).hexdigest()
        require(digest == q['allPhysicalMainSha256'][key], 'original physical interface')
        command = [str(ROOT.parent/'toolchain/jdk-25.0.4/bin/javap'),'-v','-p','-classpath',str(jar),member[:-6].replace('/','.')]
        raw = subprocess.check_output(command,text=True)
        flags = next((s.strip() for s in raw.splitlines() if s.strip().startswith('flags:')),'')
        require('ACC_INTERFACE' in flags and 'ACC_ABSTRACT' in flags and 'Code:' not in raw, 'abstract interface without executable code')
        declarations[key] = dict(classSha256=digest, classFlags=flags, javapCommand=command, actualExit=0,
                                 javapOutputSha256=hashlib.sha256(raw.encode()).hexdigest(), coverage100Claim=False)
    return dict(counters=rows, emptyDeclarations=declarations, absentCounters='N_A_NOT_SYNTHESIZED')


def text(node, path):
    value = node.findtext(path, namespaces=NS)
    require(value is not None, 'explicit POM field '+path)
    return value.strip()


def foundation(q):
    root = ET.parse(ROOT/'pom.xml').getroot()
    require(text(root,'m:groupId') == 'dev.codex.schubert' and text(root,'m:artifactId') == 'schubert-nk', 'fixed NK root')
    modules = [v.text.strip() for v in root.findall('m:modules/m:module',NS)]
    expected = ['program/characterization', *['src/schubert-nk-'+m for m in ('protocol','storage','bootstrap','api','web','batch')]]
    require(modules == expected, 'six Production modules and separate existing Characterization')
    props = {v.tag.rsplit('}',1)[-1]:v.text for v in root.find('m:properties',NS)}
    require(props['maven.compiler.release'] == '25' and props['project.build.sourceEncoding'] == 'UTF-8', 'Java25 UTF8')
    require((props['error-prone.version'],props['nullaway.version'],props['jspecify.version']) == ('2.50.0','0.14.1','1.0.1'), 'fixed actual shared null toolchain')
    require(text(root,'.//m:requireJavaVersion/m:version') == '[25,26)'
            and text(root,'.//m:requireMavenVersion/m:version') == '[3.9.12,4)'
            and root.find('.//m:dependencyConvergence',NS) is not None, 'Enforcer runtime and dependency convergence')
    args = [v.text for v in root.findall('.//m:compilerArgs/m:arg',NS)]
    require('-Xlint:all' in args and '-Werror' in args and any('NullAway:ERROR' in a and 'JSpecifyMode=true' in a for a in args), 'real lint/null failure gates')
    version = text(root,'m:version')
    managed = {}
    for dependency in root.findall('m:dependencyManagement/m:dependencies/m:dependency',NS):
        raw = text(dependency,'m:version')
        resolved = props.get(raw[2:-1]) if raw.startswith('${') and raw.endswith('}') else raw
        key = (text(dependency,'m:groupId'),text(dependency,'m:artifactId'))
        require(key not in managed,'no duplicate managed dependency')
        managed[key] = resolved
    require(managed == MANAGED,'SSC098 exact approved cross-role logging/null-version matrix')
    pom_paths = ['pom.xml']
    dependencies = {}
    for module in ALLOWED:
        path = 'src/schubert-nk-'+module+'/pom.xml'
        pom_paths.append(path)
        node = ET.parse(ROOT/path).getroot()
        local = node.find('m:properties',NS)
        values = {**props, 'project.version':version, **({v.tag.rsplit('}',1)[-1]:v.text for v in local} if local is not None else {})}
        internal = set()
        declared = []
        for dependency in node.findall('m:dependencies/m:dependency',NS):
            group, artifact = [text(dependency,'m:'+k) for k in ('groupId','artifactId')]
            scope = dependency.findtext('m:scope','compile',NS).strip()
            raw = dependency.findtext('m:version',None,NS)
            resolved = raw
            if raw and raw.startswith('${') and raw.endswith('}'):
                resolved = values.get(raw[2:-1])
            if group == 'dev.codex.schubert':
                require(resolved == version and artifact.startswith('schubert-nk-'), 'same-project fixed library')
                if scope != 'test':internal.add(artifact.removeprefix('schubert-nk-'))
            elif raw is not None:
                require(resolved and '${' not in resolved and not any(c in resolved for c in '[](),')
                        and resolved not in ('LATEST','RELEASE') and 'SNAPSHOT' not in resolved, 'external versions fixed, no ranges/fallback')
            else:
                require((group,artifact) in MANAGED, 'only explicit fixed parent dependencyManagement omission')
                resolved = MANAGED[(group,artifact)]
            declared.append(dict(groupId=group,artifactId=artifact,scope=scope,version=resolved))
        require(internal == ALLOWED[module], 'closed actual module dependency set')
        require(node.find('m:repositories',NS) is None and node.find('m:pluginRepositories',NS) is None, 'no extra repositories')
        require(text(node,'.//m:systemPropertyVariables/m:user.language') == 'ja'
                and text(node,'.//m:systemPropertyVariables/m:user.country') == 'JP'
                and text(node,'.//m:systemPropertyVariables/m:user.timezone') == 'Asia/Tokyo', 'fixed PT locale/timezone')
        dependencies[module] = declared
    require(root.find('m:repositories',NS) is None and root.find('m:pluginRepositories',NS) is None, 'no added root repository')
    wrapper = '.mvn/wrapper/maven-wrapper.properties'
    require('distributionUrl=https://repo.maven.apache.org/maven2/org/apache/maven/apache-maven/3.9.12/apache-maven-3.9.12-bin.zip\n'
            in (ROOT/wrapper).read_text(), 'fixed Maven Wrapper distribution')
    physical = 0
    for module in ALLOWED:
        jar = W/('pg6932-original4222-artifacts-v1/jars/schubert-nk-'+module+'.jar')
        with zipfile.ZipFile(jar) as zipped:
            for name in zipped.namelist():
                if name.endswith('.class'):
                    data = zipped.read(name)
                    require(data[:4] == b'\xca\xfe\xba\xbe' and int.from_bytes(data[6:8],'big') == 69
                            and hashlib.sha256(data).hexdigest() == q['allPhysicalMainSha256'][module+':'+name], 'every actual original Main targetsJava25')
                    physical += 1
    require(physical == 1669, 'all physical class versions checked')
    tc = ROOT.parent/'toolchain'
    java = tc/'jdk-25.0.4/bin/java'
    maven = tc/'m2/wrapper/dists/apache-maven-3.9.12/6068d197/bin/mvn'
    env = {'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','JAVA_HOME':str(java.parents[1]),'MAVEN_SKIP_RC':'true'}
    versions = []
    for command, expected_version in (([str(java),'-version'],'25.0.4'),([str(maven),'-o','--version'],'Apache Maven 3.9.12')):
        done = subprocess.run(command,cwd=ROOT,env=env,capture_output=True,text=True,timeout=30)
        output = done.stdout+done.stderr
        require(done.returncode == 0 and expected_version in output, 'read-only local reproduction version, not old build runtime substitution')
        versions.append(dict(command=command,actualExit=done.returncode,output=output,outputSha256=hashlib.sha256(output.encode()).hexdigest()))
    return dict(pomPaths=pom_paths,wrapperPath=wrapper,dependencies=dependencies,realPhysicalClassVersions=1669,
                majorVersion=69,originalCommand=q['command'],originalOs=q['os'],originalStartUTC=q['startUTC'],originalEndUTC=q['endUTC'],
                localReproductionVersions=versions, originalBuildRepeated=False, F03Accepted=False,
                globalCoverage100=False, formalRootCleanVerifyClaim=False)


def witness():
    prior_register = json.loads(PRIOR.read_bytes())
    initial.verify_register(prior_register)
    prior_proof = json.loads((ROOT/prior_register['witness']['path']).read_bytes())
    require(all(hashlib.sha256(initial.git('origin/main',p)).hexdigest() == h == sha(ROOT/p)
                for p,h in prior_proof['canonicalDesignHashes'].items()),'prior five criterion designs still canonical, no stale requirements')
    qp,q,cases = read_whole()
    require(sha(qp) == '728682a9eb414a4d4ef08abb84bcbd9237a8269a35a82d0f86c5bce97d596731', 'actual same-source original4222')
    tasks = {t['id']:t for t in json.loads((PMO/'481_PGPT詳細WBS.json').read_bytes())['tasks'] if t['id'] in IDS}
    inventory = json.loads((PMO/'485_WBS網羅性・受入対応.json').read_bytes())['currentPhysicalCandidate']
    suites = {}
    paths = []
    designs = {p for t in tasks.values() for p in t['evidencePlan']['designFiles']}
    designs.update(('documents/200_UI/210_アーキテクチャ/212_コンポーネント・接続設計.md',
                    'documents/200_UI/230_インターフェース/231_MQ論理構成設計.md',
                    'documents/100_RD/110_総則・方針/111_システム化方針.md',
                    'documents/100_RD/130_インターフェース要件/131_MQインターフェース要件.md'))
    for rid, task in tasks.items():
        selected = [selector(p) for p in task['evidencePlan']['candidateTestFiles']]
        suites[rid] = sorted(set(selected + list(EXTRA[rid])))
        paths.extend(task['ownedArtifacts'])
    paths.extend(SUPPORT)
    test_paths = {s:initial.suite_path(s)[2] for values in suites.values() for s in values}
    paths += list(test_paths.values())
    f02 = foundation(q)
    paths += f02['pomPaths'] + [f02['wrapperPath'], 'mvnw']
    inputs = initial.bind_archive(paths)
    for path in designs:
        require(initial.git('origin/main',path) == (ROOT/path).read_bytes(), 'current canonical design')
    joins = {s:initial.join_suite(s,(ROOT/p).read_text(),cases) for s,p in test_paths.items()}
    static_path = BASE/'PG6936-current4222-static-v1/manifest.json'
    require(sha(static_path) == 'e6de32cbea868ca65b56a1caf9cbf428aa51dcf00ec996577c28823a5b5631f8','same-source unfiltered static')
    static = json.loads(static_path.read_bytes());raw = static_path.with_name(static['inventoryFile'])
    require(sha(raw) == static['inventorySha256'],'original static rows')
    findings = json.loads(raw.read_bytes())
    arch_path = BASE/'PG6960-archunit-static-v1/manifest.json'
    require(sha(arch_path) == '7f80c3f1b1f1356ba51ada7f6c7dc55dfe82756072edcf3c7e88dcc164bbbb1f','new actual ArchUnit proof')
    arch = json.loads(arch_path.read_bytes())
    require(arch['source'] == SOURCE and arch['actualExit'] == 0 and len(arch['canaries']) == 11
            and arch['staticResult']['result']['physical'] == arch['staticResult']['result']['imported'] == 1669
            and not arch['staticResult']['result']['findings'],'all1669 static0 and independent11canaries')
    rows = {}
    for rid,task in tasks.items():
        owned, support = scope_rows(task,inventory['artifacts'],inputs)
        all_owned = {**owned, **{a['path']:a['sha256'] for a in support}}
        relevant = [v for v in findings if v['sourcePath'] in all_owned]
        require(all(v['currentWholeSource'] == SOURCE and v['sourceSha256'] == inputs[v['sourcePath']]
                    and v['status'] in ('REQUIRED_CONTRACT','CONTEXT_NOT_APPLICABLE','FALSE_POSITIVE') for v in relevant),'no unreviewed target static rows')
        shared = []
        for clazz in task['sharedClassReferences']:
            match = [a for a in inventory['artifacts'] if a.get('class') == clazz]
            require(len(match) == 1 and match[0]['owner'] == 'WBS-P005-03','explicit shared owner, no duplicate cost')
            a = match[0]
            require(inputs[a['path']] == a['sha256'],'shared source fixed')
            shared.append(dict(owner=a['owner'],path=a['path'],sha256=a['sha256'],referenceCost=0))
        rows[rid] = dict(scopePaths=task['ownedArtifacts'],requirementIds=task['requirementIds'],dependencies=task['dependencies'],
                         sharedReferences=shared,ownedHashes=owned,implementationSupport=support,
                         actualCounters={p:family(p,q) for p in all_owned if '/src/main/java/' in p},
                         originalSuiteRefs=suites[rid],originalCases=sum(len(joins[s]) for s in suites[rid]),
                         staticFindingIds=[v['findingId'] for v in relevant],criteriaExpected=task['acceptanceChecks'],
                         status='EVIDENCE_READY_REVIEW_REQUIRED')
    require(sum(len(v['scopePaths']) for v in rows.values()) == 44,'44 actual Production files, no vacuous F02 Java claim')
    require(sum(len(v['implementationSupport']) for v in rows.values()) == 2,'existing two support Main are also fully qualified')
    return dict(actualExit=0,source=SOURCE,run='PG6930-six-v1',rows=rows,allInputHashes=inputs,originalSuiteJoins=joins,
                priorRegister=dict(path=str(PRIOR.relative_to(ROOT)),sha256=sha(PRIOR)),foundation=f02,
                archunit=dict(path=str(arch_path.relative_to(ROOT)),sha256=sha(arch_path)),
                canonicalDesignHashes={p:sha(ROOT/p) for p in sorted(designs)},
                semanticReviewPath=REVIEW,semanticReviewSha256=sha(ROOT/REVIEW),
                historicalStateHashes={n:sha(PMO/n) for n in ('481_PGPT詳細WBS.json','484_WBSコスト枠・細分化.json','485_WBS網羅性・受入対応.json','486_WBS現行実績.json')},
                logicalOwnedFiles=44,implementationSupportFiles=2,actualOwnedFiles=46,logicalScopeChanged=False,additionalBudgetPp=0,
                testsExecuted=0,wholeReplayed=False,vmActions=0,formalUpdated=False,effortPercent=None,ptAlternativeCompleted=0,
                acceptance='NOT_APPLIED',toolSha256=sha(Path(__file__)))


def verify_register(register):
    require(register['source'] == SOURCE and register['formalUpdated'] is False and register['wholeEffortCompletionRate'] is None
            and register['reviewState'] == 'COMPLETE' and register['acceptedBy'], 'explicit bounded same-source PG review')
    prior = json.loads(PRIOR.read_bytes());initial.verify_register(prior)
    proof_path = ROOT/register['witness']['path']
    require(sha(proof_path) == register['witness']['sha256'],'exact second witness')
    proof = json.loads(proof_path.read_bytes())
    require(proof['actualExit'] == 0 and proof['source'] == SOURCE and proof['acceptance'] == 'NOT_APPLIED'
            and sha(ROOT/proof['semanticReviewPath']) == proof['semanticReviewSha256'],'actual immutable complete review')
    require(initial.wbs_component_overlay.historical_state_unchanged(PMO,proof['historicalStateHashes']),'no historical17 rebase/scope/cost drift')
    require(all(sha(ROOT/p) == h and initial.git(SOURCE,p) == (ROOT/p).read_bytes() for p,h in proof['allInputHashes'].items()),'current original all source/Test/POM bytes')
    states = register['records']
    require(set(states) == set(initial.IDS) | set(IDS),'exact nine, not bulk17')
    require(all(states[k] == v for k,v in prior['records'].items()),'prior five acceptances untouched')
    tasks = {t['id']:t for t in json.loads((PMO/'481_PGPT詳細WBS.json').read_bytes())['tasks'] if t['id'] in IDS}
    for rid in IDS:
        t = copy.deepcopy(tasks[rid]);row = proof['rows'][rid]
        require(row['scopePaths'] == t['ownedArtifacts'] and row['requirementIds'] == t['requirementIds']
                and row['dependencies'] == t['dependencies'],'complete unchanged local criteria scope')
        for shared in row['sharedReferences']:
            require(states[shared['owner']]['status'] == 'ACCEPTED' and states[shared['owner']]['source'] == SOURCE,'shared owner must be accepted, not just dependency label')
        t['acceptance'] = states[rid];audit.check_acceptance(t,SOURCE,states)
    require(register['newAcceptedIds'] == ['WBS-P005-01',*IDS]
            and register['revalidatedIds'] == list(initial.IDS[:-1]),'exact five new/four revalidated')
    return dict(actualExit=0,currentSourceAccepted=9,newAcceptedTotal=5,newAcceptedThisStage=4,revalidated=4,
                historical17Unchanged=True,formalUpdated=False,wholeEffortCompletionRate=None)


def main():
    parser = argparse.ArgumentParser(description=__doc__);parser.add_argument('--register',type=Path);args=parser.parse_args()
    if args.register:
        print(json.dumps(verify_register(json.loads(args.register.read_bytes()))));return
    result = witness();os.umask(0o077);OUT.mkdir()
    path = OUT/'manifest.json'
    with path.open('x') as stream:
        json.dump(result,stream,ensure_ascii=False,sort_keys=True,indent=2);stream.write('\n');stream.flush();os.fsync(stream.fileno())
    print(json.dumps(dict(actualExit=0,manifestSha256=sha(path),rows=4,uniqueOriginalCases=sum(len(v) for v in result['originalSuiteJoins'].values()),newAccepted=0)))


if __name__ == '__main__':
    main()
