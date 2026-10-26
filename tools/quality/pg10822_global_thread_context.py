"""Current2125 J2EE-only rule contexts, exact source/approved architecture; no Product or old tool execution."""
from collections import Counter
import json
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import zipfile
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = 'e73e9558971a81d30d7f81f6ab0bc5d9662667d2'
ORIGIN = '8b91944df5820535e23ba2469740f1c0aa94c447'
OUT = data.BASE/'PG10822-global-thread-context-v1'
DOCS = ('documents/300_SS/310_アプリケーション/311_モジュール・package・class責務設計.md',
    'documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md')
MODULES = ('protocol','storage','bootstrap','api','web','batch')
NS = {'m':'http://maven.apache.org/POM/4.0.0'}


def validate(rows,hashes,original_ids):
    if len(rows) != 2125 or Counter(r['id'] for r in rows) != Counter(original_ids):
        raise ValueError('every original finding once; no missing/duplicated warning')
    for row in rows:
        if row['rule'] != 'DoNotUseThreads' or row['source'] != SOURCE or hashes.get(row['path']) != row['sourceSha256']:
            raise ValueError('exact current source and single vendor rule')
        if row['disposition'] != 'CONTEXT_NOT_APPLICABLE_J2EE_RULE' or row['qualityGatePass'] or row['productTestsExecuted'] or not row['dynamicAuthorizationUnchanged']:
            raise ValueError('technical context never runtime/PT authorization or quality PASS')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    normal = data.read_checked(data.BASE/'PG10800-protocol-quality-six-compile-v1/manifest.json',
        'ee02e1c29144a78486897564d0840a86c90bfe96f6fd19f5f75af8fbe4d311b4')
    assert normal['source'] == SOURCE and normal['actualExit'] == normal['testsExecuted'] == 0
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    assert subprocess.check_output(['git','rev-parse','origin/main'],cwd=data.ROOT,text=True).strip() == ORIGIN
    approved = {p:subprocess.check_output(['git','show',ORIGIN+':'+p],cwd=data.ROOT) for p in DOCS}
    assert 'Library jar' in approved[DOCS[0]].decode() and 'Executable jar' in approved[DOCS[0]].decode()
    assert '共用起動library' in approved[DOCS[0]].decode() and 'Java processを直接ExecStart' in approved[DOCS[1]].decode()
    assert all((data.ROOT/p).read_bytes() == raw for p,raw in approved.items())
    roles = {}
    for module in MODULES:
        p = 'src/schubert-nk-'+module+'/pom.xml'
        raw = (data.ROOT/p).read_bytes()
        assert data.sha(raw) == hashes[p]
        node = ET.fromstring(raw)
        assert node.findtext('m:packaging','jar',NS) == 'jar'
        dependencies = [d.findtext('m:groupId','',NS)+':'+d.findtext('m:artifactId','',NS) for d in node.findall('m:dependencies/m:dependency',NS)]
        assert not any(d.startswith(('jakarta.platform:','jakarta.ejb:','javax.ejb:','javax:javaee')) for d in dependencies)
        plugins = [x.text for x in node.findall('.//m:plugin/m:artifactId',NS)]
        assert 'maven-war-plugin' not in plugins and 'maven-ear-plugin' not in plugins and 'maven-ejb-plugin' not in plugins
        roles['schubert-nk-'+module] = dict(packaging='jar',sourcePomSha256=hashes[p],dependencies=dependencies,
            approvedRole='STANDALONE_JAVA_SERVICE' if module in ('api','web','batch') else 'LIBRARY_ONLY_IN_STANDALONE_GRAPH')
    descriptor_names = {'ejb-jar.xml','application.xml','web.xml','application-client.xml','ra.xml'}
    assert not any(p.startswith('src/') and Path(p).name in descriptor_names for p in hashes)
    vendor = data.ROOT.parent/'toolchain/static-gates-20261015/pmd-bin-7.28.0/lib/pmd-java-7.28.0.jar'
    assert data.sha(vendor.read_bytes()) == '068b2b5fb276559c32d52e3675d297a458bf27fe181b675cee10555a55c131bd'
    with zipfile.ZipFile(vendor) as jar:
        resource = jar.read('category/java/multithreading.xml')
    node = next(n for n in ET.fromstring(resource) if n.get('name') == 'DoNotUseThreads')
    description = ''.join(node.find('{http://pmd.sourceforge.net/ruleset/2.0.0}description').itertext()).strip()
    assert 'J2EE specification' in description and 'J2EE server' in description
    raw_path = data.BASE/'PG10690-current-global-static-post-v1/findings.json'
    assert data.sha(raw_path.read_bytes()) == '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966'
    original = json.loads(raw_path.read_bytes())
    selected = [r for r in original if r['rule'] == 'DoNotUseThreads']
    assert len(original) == 9409 and len(selected) == 2125
    assert Counter(r['sourceKind'] for r in selected) == Counter(MAIN=252,TEST=1873)
    assert len({r['path'] for r in selected}) == 534
    protocol = data.read_checked(data.BASE/'PG10810-protocol-static-context-v1/manifest.json',
        '1fd906c89fcff0804b8f4fb6b3644c850b1e9103108b89048246daf2ef1afadb')
    protocol_rows = data.read_checked(data.BASE/'PG10810-protocol-static-context-v1/contexts.json',protocol['contextsSha256'])
    reused = {r['originalFindingId']:r for r in protocol_rows if r['rule'] == 'DoNotUseThreads'}
    assert set(reused) == {'PMD-06789','PMD-06790'}
    history_path = data.BASE/'PG3710-pmd-first-triage-v1/manifest.json'
    history = json.loads(history_path.read_bytes())
    old_rows = data.read_checked(history_path.parent/'dispositions239.json',history['findingDispositionPublicSha256'])
    old_thread = [r for r in old_rows if r['rule'] == 'DoNotUseThreads']
    assert len(old_thread) == 238
    rows = []
    for row in selected:
        path = row['path']
        module = Path(path).parts[1]
        assert module in roles and row['sourceKind'] in ('MAIN','TEST')
        assert ('/src/main/java/' if row['sourceKind'] == 'MAIN' else '/src/test/java/') in path
        current = hashes[path]
        if row['id'] in reused:
            assert reused[row['id']]['sourceSha256'] == current and reused[row['id']]['source'] == SOURCE
            status = 'REUSE_ALREADY_QUALIFIED_PROTOCOL_CONTEXT'
            references = ['PG10810',row['id']]
        else:
            assert row['inputSha256'] == current
            equivalent = [old for old in old_thread if old['path'] == path and old['sourceSha256'] == current
                and old['coordinates'] == {k:v for k,v in row['attributes'].items() if k != 'rule'}]
            same_path = [old for old in old_thread if old['path'] == path]
            status = 'EXACT_HISTORICAL_INPUT_CONTEXT_REUSE' if equivalent else (
                'CURRENT_INPUT_REAUTHENTICATION_PRIOR_SOURCE_OR_COORDINATES_DIFFER' if same_path else
                'CURRENT_SCOPE_NOT_MATCHED_TO_OLD238_REFERENCE_NO_NEW_WBS_CREDIT')
            references = [old['id'] for old in equivalent] or [old['id'] for old in same_path]
        rows.append(dict(id=row['id'],originalRowSha256=row['rowSha256'],originalInputSha256=row['inputSha256'],
            path=path,source=SOURCE,sourceSha256=current,rule=row['rule'],coordinates=row['attributes'],sourceKind=row['sourceKind'],
            module=module,approvedRole=roles[module]['approvedRole'],classificationWork=status,historicalReferences=references,
            disposition='CONTEXT_NOT_APPLICABLE_J2EE_RULE',basis='Exact current input in approved standalone/library graph; primary vendor explicitly requires managed J2EE threads',
            qualityGatePass=False,productTestsExecuted=0,dynamicAuthorizationUnchanged=True,threadLivenessProven=False))
    validate(rows,hashes,[r['id'] for r in selected])
    assert sum(r['classificationWork'] == 'REUSE_ALREADY_QUALIFIED_PROTOCOL_CONTEXT' for r in rows) == 2
    assert sum(r['originalInputSha256'] == r['sourceSha256'] for r in rows) == 2123
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'architecture.json',dict(source=SOURCE,originMain=ORIGIN,approvedDocumentSha256={p:data.sha(v) for p,v in approved.items()},
        moduleRoles=roles,noManagedDeploymentDescriptors=True,descriptorSourceInventorySha256=data.sha(json.dumps(sorted(hashes)).encode()),
        vendorJarSha256=data.sha(vendor.read_bytes()),vendorRuleResourceSha256=data.sha(resource),vendorDescription=description,
        actualVmOrServiceConfigurationObserved=False,allCurrentInputHashes=hashes))
    data.write(OUT/'dispositions.json',rows)
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        originalIndexSha256=data.sha(raw_path.read_bytes()),originalRawAllFindings=9409,rawThreadFindings=2125,
        main=252,test=1873,sourceFiles=534,alreadyQualifiedProtocolReused=2,remainingCurrentUnchangedInputRows=2123,
        workClassificationCounts=dict(Counter(r['classificationWork'] for r in rows)),old238ManifestSha256=data.sha(history_path.read_bytes()),
        architectureSha256=data.sha((OUT/'architecture.json').read_bytes()),dispositionsSha256=data.sha((OUT/'dispositions.json').read_bytes()),
        judgement='PG-D683',rawFindingsRemoved=0,suppressionsAdded=False,sourceChanged=False,productTestsExecuted=0,
        dynamicAuthorizationUnchanged=True,wholeF03Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None,externalActions=0))
    print(json.dumps(dict(actualExit=0,raw=2125,workClassificationCounts=dict(Counter(r['classificationWork'] for r in rows)),
        manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
