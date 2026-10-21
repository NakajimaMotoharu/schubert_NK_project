"""Own interface-proxy readiness graphs; separate API/Web counterexamples and fixed-oracle green."""
import argparse
import json
import subprocess
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6054_expiry_read_qualification import qualify
import finite_selected_profile as profile
import finite_original_red as original

OLD = '8d77b1698d543bb54548611fdf1883b6d7711358'
RED_SOURCE = None
TESTS = {
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/dispatch/ApiReadinessFailureGraph330Test.java',
 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebReadinessFailureGraph330Test.java'}
GRAPH_TESTS = {
 'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/error/ApiStartupGraph330Test.java',
 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebStartupGraph330Test.java'}
MAINS = {
 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/dispatch/ApiDependencyReadiness.java',
 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/error/TemporaryInfrastructureException.java',
 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebDependencyReadiness.java',
 'src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebStartupException.java'}
API = {'api': {'api.dispatch.ApiReadinessFailureGraph330Test'}}
WEB = {'web': {'web.bootstrap.WebReadinessFailureGraph330Test'}}
PROFILES = {
 'api-red': ('pg6562-readiness-api-red-v1', (15,8), API),
 'web-red': ('pg6564-readiness-web-red-v1', (15,8), WEB),
 'green': ('pg6566-readiness-graph-green-v1', (24,11), {
   'api': API['api'] | {'api.error.ApiStartupGraph330Test'},
   'web': WEB['web'] | {'web.bootstrap.WebStartupGraph330Test'}})}
TARGETS = {'api': ['api/dispatch/ApiDependencyReadiness','api/error/TemporaryInfrastructureException'],
           'web': ['web/bootstrap/WebDependencyReadiness','web/bootstrap/WebStartupException']}


def inventory(phase):
    return profile.inventory(PROFILES[phase][2], PROFILES[phase][1])


def guard_source(source, phase):
    p = BASE/'PG6560-auth-jdbc-qualification-v1/manifest.json'
    if sha(p) != 'df1f8652f4a3b1bb2d38af06d8162d9d455bc071e7d1498f0f0a5b8339d747c8':
        raise ValueError('genuine original auth15 qualification first')
    q = json.loads(p.read_bytes())
    if q['source'] != OLD or q['actualExit'] != 0: raise ValueError('exact prior Main source')
    changes = set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines())
    if changes != (TESTS | GRAPH_TESTS | MAINS if phase == 'green' else TESTS):
        raise ValueError('independent two Test paths / four Main and two pure new graph Test only')
    if subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','program/characterization','tools/quality/static'],cwd=ROOT):
        raise ValueError('fixed build/gates/Current')
    if phase == 'green' and (RED_SOURCE is None or subprocess.check_output(
            ['git','diff',RED_SOURCE,source,'--',*sorted(TESTS)],cwd=ROOT)):
        raise ValueError('fixed independent original readiness Test bytes')


def read_red():
    methods = ('ready330001DbGraphsPreserveFatalAfterOneCloseAndNeverOpenJms',
               'ready330002JmsLinkedAndBothCloseGraphsPreserveFatalAfterCleanup')
    rows = {}
    for phase, cls, exc, counts, notrun in (
      ('api-red','api.dispatch.ApiReadinessFailureGraph330Test','java.lang.IllegalStateException',(9,5),6),
      ('web-red','web.bootstrap.WebReadinessFailureGraph330Test',
       'dev.codex.schubert.nk.web.bootstrap.WebStartupException',(13,6),2)):
        name = 'dev.codex.schubert.nk.'+cls
        message = 'Unexpected exception type thrown, expected: <java.lang.AssertionError> but was: <'+exc+'>'
        rows[phase] = original.inspect(W/PROFILES[phase][0], lambda s: guard_source(s,phase), counts,
            {(name,m):message for m in methods}, TESTS, notrun)
    if (len({r['source'] for r in rows.values()}) != 1
            or rows['api-red']['TestHashes'] != rows['web-red']['TestHashes']):
        raise ValueError('same original Main/Test source across both module reds')
    value = dict(actualExit=0, source=rows['api-red']['source'], originals=rows,
        expectedFailures=[[p,*key] for p,r in rows.items() for key in r['expectedFailures']],
        testsExecutedByReader=0, formalAccepted=False, ptAlternativeCompleted=0, vmActions=0)
    print(json.dumps(original.publish(value, BASE/'PG6562-readiness-original-red-v1')))


def qualify_green():
    run=W/PROFILES['green'][0]; source=json.loads((run/'begin.safe.json').read_bytes())['source']
    guard_source(source,'green'); cases,_=inventory('green')
    return qualify(source,run,cases,(24,11),MAINS,
        BASE/'PG6560-auth-jdbc-qualification-v1/manifest.json',
        'df1f8652f4a3b1bb2d38af06d8162d9d455bc071e7d1498f0f0a5b8339d747c8',
        W/'pg6560-auth-jdbc-qualification-v1/manifest.safe.json',
        W/'pg6560-auth-jdbc-qualification-v1/findings.safe.json',
        'pg6568-readiness-qualification-v1','PG6568-readiness-qualification-v1',expected_phase_exits=(0,0,0))


def main():
    p=argparse.ArgumentParser();p.add_argument('phase',choices=(*PROFILES,'read-red','qualify-green'))
    phase=p.parse_args().phase
    if phase=='read-red':return read_red()
    if phase=='qualify-green':return qualify_green()
    cases,counts=inventory(phase)
    return profile.execute(PROFILES[phase][0],lambda s:guard_source(s,phase),cases,counts,PROFILES[phase][1],TARGETS)


if __name__=='__main__':raise SystemExit(main())
