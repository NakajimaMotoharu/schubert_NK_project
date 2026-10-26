"""Independent component quality: original102/PT counters, ten precise contexts,176SpotBugs; no replay."""
from collections import Counter
import copy
from pathlib import Path
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = 'e73e9558971a81d30d7f81f6ab0bc5d9662667d2'
OUT = data.BASE/'PG10814-protocol-component-quality-post-v1'
EXPECTED = {
    'PMD-06783':('UseConcurrentHashMap','PayloadCodec.java','values'),
    'PMD-06784':('CompareObjectsWithEquals','FailedJmsIsolationException.java',None),
    'PMD-06785':('CompareObjectsWithEquals','UnconfirmedJmsRollbackException.java',None),
    'PMD-06789':('DoNotUseThreads','PayloadGoldenVectorTest.java','executor'),
    'PMD-06790':('DoNotUseThreads','PayloadGoldenVectorTest.java',None),
    'PMD-06829':('UseConcurrentHashMap','IndependentNamedFieldOracle.java','accessors'),
    'PMD-06830':('UseConcurrentHashMap','IndependentNamedFieldOracle.java','areas'),
    'PMD-06831':('UseConcurrentHashMap','IndependentNamedFieldOracle.java','reviewed'),
    'PMD-06833':('NullAssignment','IndependentNamedFieldOracle.java',None),
    'PMD-06834':('UseConcurrentHashMap','IndependentNamedFieldOracle.java','absent')}


def contract(rows,hashes):
    if len(rows) != 10 or Counter(r['originalFindingId'] for r in rows) != Counter(EXPECTED.keys()):
        raise ValueError('all ten distinct original findings required')
    for row in rows:
        key = row['originalFindingId']
        if (row['rule'],Path(row['path']).name,row['actualAttributes'].get('variable')) != EXPECTED[key]:
            raise ValueError('exact rule/source/method variable context')
        if row['sourceSha256'] != hashes.get(row['path']) or row['source'] != SOURCE:
            raise ValueError('stale source')
        if row['disposition'] != 'NOT_APPLICABLE_EXACT_SOURCE_CONTEXT' or row['scopeGeneralized'] or row['rawSuppressed'] or row['newProductExecutions']:
            raise ValueError('no blanket exemption or invented test execution')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    context_path = data.BASE/'PG10810-protocol-static-context-v1/manifest.json'
    context = data.read_checked(context_path,'1fd906c89fcff0804b8f4fb6b3644c850b1e9103108b89048246daf2ef1afadb')
    proof_path = data.BASE/'PG10808-protocol-quality-post-v1/manifest.json'
    proof = data.read_checked(proof_path,'d19e6b96aab7c1487bef2757d1f2b5b312d41fc2a6995d977c2ff0c0a8b0fda5')
    bugs_path = data.BASE/'PG10813-protocol-spotbugs-recovery-v1/manifest.json'
    bugs = data.read_checked(bugs_path,'0b63b171693052705c3ffe9051edc7bb3d608d3b8498c3305e3de11b6e581370')
    normal_path = data.BASE/'PG10800-protocol-quality-six-compile-v1/manifest.json'
    normal = data.read_checked(normal_path,'ee02e1c29144a78486897564d0840a86c90bfe96f6fd19f5f75af8fbe4d311b4')
    prepared = data.read_checked(data.BASE/'PG10802-protocol-quality-preflight-v1/manifest.json',
        '8d0eaed1b32f344822bf7cdba354e8272de1d4340fbd2fc6bca8f942cb17cd58')
    assert all(r['source'] == SOURCE and r['actualExit'] == 0 for r in (context,proof,bugs,normal,prepared))
    assert normal['terminal']['actualExit'] == normal['testsExecuted'] == 0 and len(normal['jars']) == 6
    assert proof['protocolFourCounters100'] and proof['testExecutions'] == proof['uniqueMethods'] == 102
    coverage = data.read_checked(proof_path.parent/'complete-protocol-coverage.json',proof['coverageSha256'])
    assert len(coverage) == 1 and coverage[0]['session']['sessionId'] == 'PG10804-PROTOCOL-JP'
    bundle = coverage[0]['bundleCounters']
    assert bundle == {k:dict(missed=0,covered=v) for k,v in dict(LINE=3480,METHOD=743,CLASS=159,BRANCH=1014).items()}
    assert len(coverage[0]['completeProtocolClasses']) == 169 and len(coverage[0]['nonExecutablePackageMetadata']) == 7
    assert bugs['findings'] == bugs['processingErrors'] == bugs['missingClasses'] == 0 and not bugs['mavenReplayed']
    assert bugs['allPhysicalProtocolMainClasses'] == 176 and set(bugs['analysisClassNames']) == set(prepared['completeProtocolMainClasses'])
    report = bugs_path.parent/'spotbugsXml.xml'
    assert data.sha(report.read_bytes()) == bugs['primaryReportSha256']
    root = ET.fromstring(report.read_bytes())
    assert len(root.findall('.//ClassStats')) == 176 and not root.findall('BugInstance')
    assert root.find('Errors').get('missingClasses') == root.find('Errors').get('errors') == '0'
    rows = data.read_checked(context_path.parent/'contexts.json',context['contextsSha256'])
    contract(rows,context['sourceHashes'])
    assert context['rawStaticExit'] == 1 and context['rawPmd'] == context['concreteNotApplicable'] == 10
    assert context['unclassified'] == context['applicableUnresolved'] == 0 and not context['scopeGeneralized'] and not context['suppressionsAdded']
    hashes = normal['begin']['inputHashes']
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    pom = (data.ROOT/'pom.xml').read_text()
    assert '<phase>validate</phase>' in pom and '-Xep:NullAway:ERROR' in pom and '-XepOpt:NullAway:JSpecifyMode=true' in pom
    assert '<arg>-Werror</arg>' in pom and '<arg>-Xlint:all</arg>' in pom
    bads = []
    for field,value in [('sourceSha256','0'*64),('scopeGeneralized',True),('rawSuppressed',True),('disposition','PASS')]:
        bad = copy.deepcopy(rows)
        bad[0][field] = value
        bads.append(bad)
    bads += [rows[:-1],rows+[rows[0]]]
    for bad in bads:
        try: contract(bad,context['sourceHashes'])
        except ValueError: pass
        else: raise AssertionError('invalid component qualification accepted')
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        normalManifestSha256=data.sha(normal_path.read_bytes()),runtimeProofSha256=data.sha(proof_path.read_bytes()),
        contextManifestSha256=data.sha(context_path.read_bytes()),spotbugsManifestSha256=data.sha(bugs_path.read_bytes()),
        allProtocolPhysicalMainClasses=176,currentTests=102,currentSuites=22,protocolFourCounters100=True,bundleCounters=bundle,
        rawPmd=10,exactSourceNotApplicable=10,applicableUnresolved=0,unclassified=0,checkstyle=0,
        spotbugs=0,spotbugsErrors=0,spotbugsMissingClasses=0,nullAwayEnabledByValidatedPom=True,
        sixModuleFormatAndCompileExit=0,metadataNegativeVectors=len(bads),
        qualification='PROTOCOL_COMPONENT_TECHNICAL_QUALITY_COMPLETE_WITH_10_EXACT_SOURCE_CONTEXTS',
        wholeJavaCoverage100=False,whole451Accepted=False,wholeF03Accepted=False,productTestsExecuted=0,
        newAccepted=0,formalUpdated=False,effortPercent=None,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
