"""Independent2125 original-id/input/architecture join and nine negative metadata cases; no Product execution."""
from collections import Counter
import copy
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify

SOURCE = 'e73e9558971a81d30d7f81f6ab0bc5d9662667d2'
OUT = data.BASE/'PG10824-global-thread-context-post-v1'


def contract(rows,reference,hashes,roles):
    if len(rows) != len(reference) or Counter(r['id'] for r in rows) != Counter(reference.keys()):
        raise ValueError('exact raw finding multiplicity')
    for row in rows:
        old = reference[row['id']]
        module = Path(old['path']).parts[1]
        if row['path'] != old['path'] or row['coordinates'] != old['attributes'] or row['originalRowSha256'] != old['rowSha256']:
            raise ValueError('original exact source coordinates')
        if row['rule'] != 'DoNotUseThreads' or row['source'] != SOURCE or row['sourceSha256'] != hashes.get(old['path']):
            raise ValueError('one vendor rule/exact current input')
        if row['module'] != module or row['approvedRole'] != roles.get(module) or row['sourceKind'] != old['sourceKind']:
            raise ValueError('approved module/source role')
        if row['qualityGatePass'] or row['productTestsExecuted'] or not row['dynamicAuthorizationUnchanged'] or row['threadLivenessProven']:
            raise ValueError('no invented PT, liveness, authorization or quality PASS')
        if row['disposition'] != 'CONTEXT_NOT_APPLICABLE_J2EE_RULE':
            raise ValueError('technical context status only')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    path = data.BASE/'PG10822-global-thread-context-v1/manifest.json'
    primary = data.read_checked(path,'ea2f5a8c9056874991de9a40bf9b9395ad1364be0cf3a0aca941257e855758c8')
    assert primary['source'] == SOURCE and primary['actualExit'] == 0 and primary['rawFindingsRemoved'] == 0
    rows = data.read_checked(path.parent/'dispositions.json',primary['dispositionsSha256'])
    architecture = data.read_checked(path.parent/'architecture.json',primary['architectureSha256'])
    normal = data.read_checked(data.BASE/'PG10800-protocol-quality-six-compile-v1/manifest.json',
        'ee02e1c29144a78486897564d0840a86c90bfe96f6fd19f5f75af8fbe4d311b4')
    assert normal['source'] == SOURCE and normal['actualExit'] == 0
    hashes = normal['begin']['inputHashes']
    assert architecture['allCurrentInputHashes'] == hashes
    assert all(data.sha((data.ROOT/p).read_bytes()) == h for p,h in hashes.items())
    original = data.read_checked(data.BASE/'PG10690-current-global-static-post-v1/findings.json',
        '92b57b1840edb7258e1e180b06a2f69af94fae594f9c9c549a0378b439116966')
    selected = [r for r in original if r['rule'] == 'DoNotUseThreads']
    reference = {r['id']:r for r in selected}
    assert len(selected) == len(reference) == 2125
    assert Counter(r['sourceKind'] for r in selected) == Counter(MAIN=252,TEST=1873)
    expected_roles = {'schubert-nk-'+name:('STANDALONE_JAVA_SERVICE' if name in ('api','web','batch') else 'LIBRARY_ONLY_IN_STANDALONE_GRAPH')
        for name in ('protocol','storage','bootstrap','api','web','batch')}
    assert set(architecture['moduleRoles']) == set(expected_roles)
    ns = {'m':'http://maven.apache.org/POM/4.0.0'}
    for module,role in expected_roles.items():
        record = architecture['moduleRoles'][module]
        pom_path = 'src/'+module+'/pom.xml'
        assert record['approvedRole'] == role and record['sourcePomSha256'] == hashes[pom_path]
        pom = ET.fromstring((data.ROOT/pom_path).read_bytes())
        assert pom.findtext('m:packaging','jar',ns) == 'jar'
        dependencies = [d.findtext('m:groupId','',ns)+':'+d.findtext('m:artifactId','',ns) for d in pom.findall('m:dependencies/m:dependency',ns)]
        assert dependencies == record['dependencies']
        assert not any(x.startswith(('jakarta.platform:','jakarta.ejb:','javax.ejb:','javax:javaee')) for x in dependencies)
    assert architecture['noManagedDeploymentDescriptors'] and not architecture['actualVmOrServiceConfigurationObserved']
    forbidden = {'web.xml','ejb-jar.xml','application.xml','application-client.xml','ra.xml'}
    assert not any(p.startswith('src/') and Path(p).name in forbidden for p in hashes)
    assert 'J2EE specification' in architecture['vendorDescription'] and 'J2EE server' in architecture['vendorDescription']
    assert architecture['originMain'] == '8b91944df5820535e23ba2469740f1c0aa94c447'
    for doc,digest in architecture['approvedDocumentSha256'].items():
        approved = subprocess.check_output(['git','show',architecture['originMain']+':'+doc],cwd=data.ROOT)
        assert data.sha(approved) == digest and (data.ROOT/doc).read_bytes() == approved
    contract(rows,reference,hashes,expected_roles)
    reused = {r['id'] for r in rows if r['classificationWork'] == 'REUSE_ALREADY_QUALIFIED_PROTOCOL_CONTEXT'}
    assert reused == {'PMD-06789','PMD-06790'}
    assert all(reference[r['id']]['inputSha256'] == r['sourceSha256'] for r in rows if r['id'] not in reused)
    history = data.read_checked(data.BASE/'PG3710-pmd-first-triage-v1/manifest.json',primary['old238ManifestSha256'])
    old_rows = data.read_checked(data.BASE/'PG3710-pmd-first-triage-v1/dispositions239.json',history['findingDispositionPublicSha256'])
    exact = 0
    for row in rows:
        if row['classificationWork'] == 'EXACT_HISTORICAL_INPUT_CONTEXT_REUSE':
            matched = [h for h in old_rows if h['id'] in row['historicalReferences'] and h['path'] == row['path']
                and h['rule'] == row['rule'] and h['sourceSha256'] == row['sourceSha256']
                and h['coordinates'] == {k:v for k,v in row['coordinates'].items() if k != 'rule'}]
            assert len(matched) == 1
            exact += 1
    assert exact == 43
    assert Counter(r['classificationWork'] for r in rows) == Counter(primary['workClassificationCounts'])
    bads = [rows[:-1],rows+[rows[0]]]
    for field,value in [('id','UNKNOWN'),('sourceSha256','0'*64),('rule','CloseResource'),('approvedRole','MANAGED_J2EE'),
        ('dynamicAuthorizationUnchanged',False),('qualityGatePass',True),('productTestsExecuted',1)]:
        bad = copy.deepcopy(rows)
        bad[0][field] = value
        bads.append(bad)
    for bad in bads:
        try: contract(bad,reference,hashes,expected_roles)
        except ValueError: pass
        else: raise AssertionError('incomplete/stale/foreign rule or invented quality accepted')
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'manifest.json',dict(actualExit=0,source=SOURCE,invocation=invocation,
        primaryManifestSha256=data.sha(path.read_bytes()),original2125IdsPreserved=True,rawAllFindings=9409,rawThreadFindings=2125,
        reusedAlreadyQualifiedProtocol=2,exactHistoricalReuse=43,priorSourceOrCoordinateReauthentication=193,
        notMatchedToOld238ReferenceNoNewWbsCredit=1887,metadataNegativeVectors=len(bads),
        actualProductExecutions=0,coverage=None,rawWarningsRemoved=0,unknownDynamicAuthorizationUnchanged=True,
        wholeF03Accepted=False,newAccepted=0,formalUpdated=False,effortPercent=None,externalActions=0))
    print(data.sha((OUT/'manifest.json').read_bytes()))


if __name__ == '__main__':
    main()
