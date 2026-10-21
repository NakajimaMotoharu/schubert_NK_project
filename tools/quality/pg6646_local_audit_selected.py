"""Pure primitive logger/callback red, then fixed existing owned REQUEST domains."""
import argparse
import json
import subprocess
from pg5940_private_lock_compile import ROOT,W,BASE,sha
from pg6054_expiry_read_qualification import qualify
import finite_selected_profile as profile
import finite_original_red as original

OLD='2d4633fb25e2c47b2adcbada8c932aba727f20fd'
PUBLISHED='8968f27707f518095733ce19190bb825ea18623b'
TEST='src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/logging/LocalAuditGraph331Test.java'
MAIN='src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/logging/WebRequestLogProducer.java'
TARGETS={'web':['web/logging/WebRequestLogProducer']}
SLOTS={'red':'pg6646-local-audit-red-v1','green':'pg6648-local-audit-green-v1'}


def inventory(phase):
    extra={'web.logging.LocalAuditGraph331Test'}
    if phase=='green':extra|={'web.logging.WebRequestLogProducerTest','web.logging.RequestProjectionFailureGraph329Test','web.bootstrap.WebStartupGraph330Test'}
    return profile.inventory({'web':extra},(16,8) if phase=='red' else (31,11))


def guard_source(source,phase):
    qp=BASE/'PG6634-current4158-cases/qualification.json'
    if sha(qp)!='658804678cc942c70ee498bc030d9833d8043994b43d8cffaf7fdf58accc5cb8':raise ValueError('genuine original4158 first')
    q=json.loads(qp.read_bytes())
    if q['productionSource']!=OLD or q['actualExit']!=0:raise ValueError('qualified Main baseline')
    subprocess.check_call(['git','merge-base','--is-ancestor',PUBLISHED,'origin/main'],cwd=ROOT)
    changes=set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines())
    if changes!=({TEST} if phase=='red' else {TEST,MAIN}):raise ValueError('one independent Test / one necessary Main only')
    if subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','program/characterization','tools/quality/static'],cwd=ROOT):raise ValueError('quality/build/Current gates unchanged')
    if phase=='green':
        red=json.loads((W/SLOTS['red']/'begin.safe.json').read_bytes())['source']
        if subprocess.check_output(['git','diff',red,source,'--',':(glob)src/*/src/test/**'],cwd=ROOT):raise ValueError('all new/old Test bytes fixed')


def read_red():
    cls='dev.codex.schubert.nk.web.logging.LocalAuditGraph331Test'
    names=('local331001LoggerGraphSignalsOnceBeforeOriginalFatalWithoutAnyProjection',
           'local331002TerminalGraphCannotBecomeFixedOrdinaryCatalog',
           'local331003CallbackThenLoggerGraphPriorityAndAliasesAreIndependent')
    expected={(cls,n):'expected: <true> but was: <false>' for n in names}
    result=original.inspect(W/SLOTS['red'],lambda s:guard_source(s,'red'),(14,6),expected,{TEST},2)
    print(json.dumps(original.publish(result,BASE/'PG6646-local-audit-original-red-v1')))


def qualify_green():
    run=W/SLOTS['green'];source=json.loads((run/'begin.safe.json').read_bytes())['source']
    guard_source(source,'green');cases,_=inventory('green')
    return qualify(source,run,cases,(31,11),{MAIN},
       BASE/'PG6632-jms-secondary-qualification-v1/manifest.json',
       '12b0ae457468b7c9c52d4e2ad10da8daf6084f962ffb084236c78fa76db55f87',
       W/'pg6632-jms-secondary-qualification-v1/manifest.safe.json',
       W/'pg6632-jms-secondary-qualification-v1/findings.safe.json',
       'pg6650-local-audit-qualification-v1','PG6650-local-audit-qualification-v1',expected_phase_exits=(0,0,0))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=('red','read-red','green','qualify-green'))
    phase=parser.parse_args().phase
    if phase=='read-red':return read_red()
    if phase=='qualify-green':return qualify_green()
    cases,counts=inventory(phase)
    return profile.execute(SLOTS[phase],lambda s:guard_source(s,phase),cases,counts,(16,8) if phase=='red' else (31,11),TARGETS)


if __name__=='__main__':raise SystemExit(main())
