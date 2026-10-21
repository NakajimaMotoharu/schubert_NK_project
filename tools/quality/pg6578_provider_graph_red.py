"""New own PG fixture only: provider graph counterexamples before ordinary API mapper PG."""
import argparse
import json
import subprocess
from pg5940_private_lock_compile import ROOT, W, BASE, sha
import finite_selected_profile as profile
import finite_original_red as original

OLD='f3fffb246ee1dc62389ec0085c1fd6556ad79694'
TEST='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/question/QuestionProviderFailureGraph329Test.java'
SLOT='pg6578-provider-graph-red-v1'
TARGETS={'api':['api/application/question/QuestionWorkerService']}


def inventory():
    return profile.inventory({'api':{'api.application.question.QuestionProviderFailureGraph329Test'}},(15,8))


def guard_source(source):
    qp=BASE/'PG6574-jdbc-attachment-qualification-v1/manifest.json'
    if sha(qp)!='f8fb1042d4bd310987153659d7b1e51ca95a8d6337ae3df7d0e9c830efa8c5d0':
        raise ValueError('original core31/8511667 source first')
    q=json.loads(qp.read_bytes())
    if q['source']!=OLD or q['actualExit']!=0:raise ValueError('exact previous qualified Main source')
    changes=set(subprocess.check_output(['git','diff','--name-only',OLD,source,'--','src'],cwd=ROOT,text=True).splitlines())
    if changes!={TEST}:raise ValueError('independent provider Test only, all Main and old Test unchanged')
    if subprocess.check_output(['git','diff',OLD,source,'--','pom.xml','.mvn','mvnw','program/characterization','tools/quality/static'],cwd=ROOT):
        raise ValueError('fixed build/gates/Current')


def read_red():
    name='dev.codex.schubert.nk.api.application.question.QuestionProviderFailureGraph329Test'
    message='Expected java.lang.AssertionError to be thrown, but nothing was thrown.'
    expected={(name,method):message for method in ('providerBusinessMarkerFatalCannotBecomeBusinessError',
                                                  'providerRuntimeFatalCannotBecomeFinalDlq')}
    value=original.inspect(W/SLOT,guard_source,(9,5),expected,{TEST},6)
    print(json.dumps(original.publish(value,BASE/'PG6578-provider-original-red-v1')))


def main():
    p=argparse.ArgumentParser();p.add_argument('phase',choices=('red','read-red'));phase=p.parse_args().phase
    if phase=='read-red':return read_red()
    cases,counts=inventory()
    return profile.execute(SLOT,guard_source,cases,counts,(15,8),TARGETS)


if __name__=='__main__':raise SystemExit(main())
