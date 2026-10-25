"""Source-only fixture equivalence and individual static applicability; never invokes a Test or resource."""
from collections import Counter
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET

import g07_host_class_provenance_inputs as data
from host_tool_invocation import capture, verify
import pg9906_user_query_oracle_source_post as old
import java_literal_metadata as literal

ROOT = data.ROOT
SOURCE = '4c94a7d4665e4f3c27a7d39fb2b427bec663d903'
OUT = data.BASE/'PG9912-user-query-fixture-post-v1'
LITERALS = {
    old.TEST:{'SEARCH_LAYOUT':'"USRREQ01"','DETAIL_LAYOUT':'"UDTREQ01"','ACTIVE_STATE':'"ACTIVE"'},
    old.CALLER:{'SEARCH_LAYOUT':'"USRREQ01"','SUCCESS_RESULT':'"0000"','SYSTEM_ERROR_RESULT':'"0200"',
        'FORBIDDEN_RESULT':'"0103"','NO_FAULT':'"none"','DATABASE_FAULT_POINT':'"database"',
        'INBOX_COUNT_SQL':'"select count(*) from schubert.request_inbox"',
        'FIRST_AUTH_COMMIT':'1','QUERY_RESULT_COMMIT':'2','REPLAY_AUTH_COMMIT':'3'}}
DECL = re.compile(r'private\s+static\s+final\s+(String|int)\s+([A-Z_]+)\s*=\s*("(?:\\.|[^"\\])*"|[0-9]+)\s*;')


def expand(text, expected):
    found = {m.group(2):m.group(3) for m in DECL.finditer(text)}
    if found != expected or len(list(DECL.finditer(text))) != len(expected):
        raise ValueError('exact independent local fixture literal catalog required')
    without = DECL.sub('',text)
    return old.LEX.sub(lambda m:expected.get(m.group(),m.group()),without)


def core(text, simple):
    result = literal.core_tokens(text)
    result = result[result.index('class'+simple+'{'):]
    return result.replace('intrecordLength=mode==2?1:0,recordCount=mode==2?1:0;',
        'intrecordLength=mode==2?1:0;intrecordCount=mode==2?1:0;')


def main():
    invocation = capture(Path(__file__))
    assert not OUT.exists()
    literal_vectors = literal.vectors()
    normal_path = data.BASE/'PG9908-user-query-fixture-six-compile-v1/manifest.json'
    normal = json.loads(normal_path.read_bytes())
    assert normal['actualExit'] == 0 and normal['source'] == SOURCE and normal['testsExecuted'] == 0
    raw_static = data.BASE/'PG9910-user-query-fixture-static-v1/manifest.json'
    static = json.loads(raw_static.read_bytes())
    assert static['source'] == SOURCE and static['reports']['checkstyle']['findings'] == 0
    assert all(r['processingErrors'] == 0 for r in static['reports'].values())
    prior = data.read_checked(data.BASE/'PG9866-snapshot-nonce-six-compile-v1/manifest.json',
        '2b00918c64ac9dfc7e9b4d648c93ef8ef0bee293ae1faa65cc280c3dd21ab535')
    hashes = normal['begin']['inputHashes']
    assert set(hashes) == set(prior['begin']['inputHashes'])
    assert {p for p in hashes if hashes[p] != prior['begin']['inputHashes'][p]} == {old.TEST,old.CALLER}
    assert all(data.sha((ROOT/p).read_bytes()) == h for p,h in hashes.items())
    expanded = {}
    for path,catalog in LITERALS.items():
        text = (ROOT/path).read_text()
        expanded[path] = expand(text,catalog)
        earlier = subprocess.check_output(['git','show','5f18a4e3d3f35fe58e2fdb381735200824a727d3:'+path],cwd=ROOT).decode()
        assert core(earlier,Path(path).stem) == core(expanded[path],Path(path).stem)
        wrong = dict(catalog)
        wrong['SEARCH_LAYOUT'] = '"WRONG001"'
        try:
            expand(text,wrong)
        except ValueError:
            pass
        else:
            raise AssertionError('incorrect local fixture constant accepted')
    old.oracle(expanded[old.TEST],expanded[old.CALLER])
    negatives = old.negatives(expanded[old.TEST],expanded[old.CALLER])
    assert old.jar_classes(prior) == old.jar_classes(normal)
    test = old.compact((ROOT/old.TEST).read_text())
    caller = old.compact((ROOT/old.CALLER).read_text())
    assert 'try(varcanonical=request.canonical(actor);varkeys=UserMutationRequestTest.keys())' in test
    assert 'varactual=canonical.fields().get(i);' in test
    assert 'varreceiver=factory.createContext(jakarta.jms.JMSContext.SESSION_TRANSACTED);' in caller
    assert 'returnUserApplicationFixture.invoke(receiver,m,a);' in caller
    assert 'jakarta.jms.JMSContext.class.getClassLoader()' in caller
    reasons = {
        'NullAssignment':'Test removes its injected sqlFault to restore the no-fault fixture between cases; no production null normalization or NPE catch.',
        'AvoidCatchingGenericException':'Test Runnable wraps the checked Exception declaration of fixture session/SQL setup in AssertionError; not Production broad failure recovery.',
        'DoNotUseThreads':'This class is a standalone host PT fixture, not a managed J2EE component. Existing owned worker lifetime assertions remain; no worker executed by this review.',
        'CloseResource':'Borrowed canonical.fields element is owned by enclosing try-with CanonicalRequest; JMSContext proxy borrows receiver owned by outer try-with. No new independent resource is acquired at either flagged assignment.',
        'UseProperClassLoader':'The Test proxy implements JMSContext using that interface declaring loader for type identity, not application-server context classloading.'}
    source_by_suffix = {Path(p).name:p for p in LITERALS}
    applicability, counts = [],Counter()
    xml = data.BASE/'PG9910-user-query-fixture-static-v1/pmd.xml'
    assert data.sha(xml.read_bytes()) == static['reports']['pmd']['sha256']
    for file in ET.parse(xml).getroot().iter():
        if file.tag.rpartition('}')[2] != 'file':
            continue
        path = source_by_suffix[Path(file.attrib['name']).name]
        for node in file:
            if node.tag.rpartition('}')[2] != 'violation':
                continue
            rule = node.attrib['rule']
            assert rule in reasons
            line = int(node.attrib['beginline'])
            source_lines = (ROOT/path).read_text().splitlines()
            source_line = source_lines[line-1]
            if rule == 'NullAssignment':
                assert 'f.sqlFault = null;' in source_line
            elif rule == 'AvoidCatchingGenericException':
                assert 'catch (Exception failure)' in source_line
            elif rule == 'CloseResource':
                assert ('var actual = canonical.fields().get(i);' in source_line if path == old.TEST else
                    '(jakarta.jms.JMSContext)' in '\n'.join(source_lines[line-1:line+2]))
            elif rule == 'UseProperClassLoader':
                assert 'jakarta.jms.JMSContext.class.getClassLoader()' in source_line
            elif rule == 'DoNotUseThreads':
                assert any(t in source_line for t in ('Executors.','pool.submit(','pool =','pool.submit('))
            applicability.append(dict(path=path,sourceSha256=hashes[path],rule=rule,line=line,
                status='NOT_APPLICABLE_TO_THIS_EXACT_TEST_STATEMENT',reason=reasons[rule]))
            counts[rule] += 1
    assert dict(counts) == {'NullAssignment':5,'AvoidCatchingGenericException':1,'DoNotUseThreads':6,'CloseResource':2,'UseProperClassLoader':1}
    assert static['actualExit'] == 1 and len(applicability) == static['reports']['pmd']['findings'] == 15
    verify(invocation)
    OUT.mkdir()
    data.write(OUT/'pmd-applicability.json',applicability)
    value = dict(actualExit=0,status='STATIC_ORACLE_AND_APPLICABILITY_REVIEW_COMPLETE_DYNAMIC_UNEXECUTED',source=SOURCE,
        invocation=invocation,normalManifestSha256=data.sha(normal_path.read_bytes()),rawStaticManifestSha256=data.sha(raw_static.read_bytes()),
        rawStaticExit=1,rawPmdFindings=15,rawCheckstyleFindings=0,pmdProcessingErrors=0,pmdApplicableFindings=0,
        applicabilitySha256=data.sha((OUT/'pmd-applicability.json').read_bytes()),applicabilityByRule=dict(counts),
        localFixtureLiteralsIndependentlyBound=13,coreTokensUnchangedFromCorrectedCallerCandidate=True,
        negativeMetadataVectors=negatives+2,literalMetadataVectors=literal_vectors,mainClassesUnchanged=1843,changedTestSources=2,
        originalPostPreparationFailure=dict(actualExit=1,stage='core literal split equality before target execution',
            toolSha256='80bad13476a2ec91af9f88f0ae1a3532ddd5be184ce893539d16268420408ec7',
            preservedToolPath='/home/mini/codex/project1/work/pgpt-runs/PG379/pg9912-user-query-fixture-post-initial-source.py'),
        productTestsExecuted=0,coverage=None,dynamicTestStatus='NOT_EXECUTED_DB_DEPENDENCY_HOLD',
        suppressionsAdded=False,rawFindingsRetained=True,wholeF03Accepted=False,whole451Accepted=False,
        oldDynamicSuccessTransferred=False,externalActions=0,heldValidationRetried=False,
        newAccepted=0,formalUpdated=False,effortPercent=None,bugs=['BUG1777','BUG1778','BUG1779'],horizontal=['YKT1528','YKT1529','YKT1530'])
    data.write(OUT/'manifest.json',value)
    print(json.dumps(dict(actualExit=0,rawPmd=15,applicablePmd=0,checkstyle=0,metadataNegatives=negatives+2,
        literalVectors=literal_vectors,productTests=0,manifestSha256=data.sha((OUT/'manifest.json').read_bytes()))))


if __name__ == '__main__':
    main()
