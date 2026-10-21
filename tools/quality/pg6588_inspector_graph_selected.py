"""Pure proxy regression of inspector4; existing own Inspector SQL fixtures for green only."""
import argparse
import json
import subprocess
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6054_expiry_read_qualification import qualify
import finite_selected_profile as profile
import finite_original_red as original

OLD='794207803ebc219f4ff93d4f7079a2d98da0d713'
RED_SOURCE=None
TEST='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/InspectorFailureGraph329Test.java'
NAMES={'InspectorDatabaseConnections','AuthenticationInboxInspector','NonAuthenticationInboxInspector','QuestionMutationInboxInspector'}
MAINS={'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/maintenance/'+n+'.java' for n in NAMES}
TARGETS={'api':['api/maintenance/'+n for n in sorted(NAMES)]}
SLOTS={'red':'pg6588-inspector-graph-red-v1','green':'pg6590-inspector-graph-green-v1'}


def inventory(phase):
    extra={'api.maintenance.InspectorFailureGraph329Test'}
    if phase=='green':extra|={'api.maintenance.'+n+'Test' for n in NAMES}
    return profile.inventory({'api':extra},(21,8) if phase=='red' else (60,12))


def guard_source(source,phase):
    qp=BASE/'PG6584-api-jdbc-domain-qualification-v1/manifest.json'
    if sha(qp)!='edc091088de4d1890f33a2643378f6cce9eb5da1145eda8070bcd802f3b7fe18':
        raise ValueError('original qualified256 source first')
    q=json.loads(qp.read_bytes())
    if q['source']!=OLD or q['actualExit']!=0:raise ValueError('exact baseline Main identity')
    changes=set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines())
    if changes!=({TEST} if phase=='red' else {TEST}|MAINS):raise ValueError('one pure Test / exactly four reviewed inspector Main')
    if subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','program/characterization','tools/quality/static'],cwd=ROOT):
        raise ValueError('fixed build/static/Current')
    if phase=='green' and (RED_SOURCE is None or subprocess.check_output(
            ['git','diff',RED_SOURCE,source,'--',':(glob)src/*/src/test/**'],cwd=ROOT)):
        raise ValueError('fixed original nine Test and all old oracle bytes')


def read_red():
    name='dev.codex.schubert.nk.api.maintenance.InspectorFailureGraph329Test'
    methods=['inspector329001ConnectorGraphCannotBecomeUnavailable',
             'inspector329002AdmissionGraphClosesOnceBeforeFatalEscapes',
             'inspector329003DirectPrimaryAndCleanupFatalIdentitiesStayDistinct']
    message=('Unexpected exception type thrown, expected: <java.lang.AssertionError> '
             'but was: <java.sql.SQLNonTransientConnectionException>')
    expected={(name,m):message for m in methods}
    expected[(name,'inspector329004NonFatalCyclesAndSameThrowableKeepExistingOutcomes')]=(
        'Unexpected exception type thrown, expected: <java.lang.IllegalStateException> '
        'but was: <java.sql.SQLNonTransientConnectionException>')
    for method in ('inspector329007AuthenticationFalseMapperMustPreserveFatal',
                   'inspector329008NonAuthenticationFalseMapperMustPreserveFatal',
                   'inspector329009QuestionMutationFalseMapperMustPreserveFatal'):
        expected[(name,method)]='Expected java.lang.AssertionError to be thrown, but nothing was thrown.'
    value=original.inspect(W/SLOTS['red'],lambda s:guard_source(s,'red'),(15,5),expected,{TEST},6)
    print(json.dumps(original.publish(value,BASE/'PG6588-inspector-original-red-v1')))


def qualify_green():
    run=W/SLOTS['green'];source=json.loads((run/'begin.safe.json').read_bytes())['source']
    guard_source(source,'green');cases,_=inventory('green')
    return qualify(source,run,cases,(60,12),MAINS,
        BASE/'PG6584-api-jdbc-domain-qualification-v1/manifest.json',
        'edc091088de4d1890f33a2643378f6cce9eb5da1145eda8070bcd802f3b7fe18',
        W/'pg6584-api-jdbc-domain-qualification-v1/manifest.safe.json',
        W/'pg6584-api-jdbc-domain-qualification-v1/findings.safe.json',
        'pg6592-inspector-qualification-v1','PG6592-inspector-qualification-v1',expected_phase_exits=(0,0,0))


def main():
    p=argparse.ArgumentParser();p.add_argument('phase',choices=('red','read-red','green','qualify-green'))
    phase=p.parse_args().phase
    if phase=='read-red':return read_red()
    if phase=='qualify-green':return qualify_green()
    cases,counts=inventory(phase)
    return profile.execute(SLOTS[phase],lambda s:guard_source(s,phase),cases,counts,
                           (21,8) if phase=='red' else (60,12),TARGETS)


if __name__=='__main__':raise SystemExit(main())
