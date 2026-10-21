"""Own finite SQL/JMS fixtures, fixed provider oracle and existing API domains; no VM access."""
import argparse
import json
import subprocess
from pg5940_private_lock_compile import ROOT, W, BASE, sha
from pg6054_expiry_read_qualification import qualify
from pg6580_api_mapper_plan import SOURCE
import finite_selected_profile as profile

RED_SOURCE='d925f25cf8c55a4fa70ecb61ac334fdb9802c77b'
TEST='src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/question/QuestionProviderFailureGraph329Test.java'
SLOT='pg6582-api-jdbc-domain-green-v1'
EXPECTED=(256,39)
API={
 'api.application.admin.UserCommandServiceTest','api.application.admin.UserMutationApplicationServiceTest',
 'api.application.admin.UserQueryApplicationServiceTest','api.application.log.LogQueryApplicationServiceTest',
 'api.application.media.MediaApplicationServiceTest','api.application.question.QuestionCommandServiceTest',
 'api.application.question.QuestionMutationApplicationServiceTest','api.application.question.QuestionQueryApplicationServiceTest',
 'api.application.question.QuestionSubmissionServiceTest','api.application.question.QuestionSubmissionBoundaryRemainderTest',
 'api.application.question.QuestionWorkerServiceTest','api.application.question.QuestionProviderFailureGraph329Test',
 'api.application.scenario.ScenarioApplicationServiceTest','api.idempotency.JdbcInboxCoordinatorTest',
 'api.logging.WebLogIngestServiceTest','api.maintenance.AuthenticationInboxCleanupTest',
 'api.maintenance.QuestionQueryInboxCleanupTest','api.messaging.outbound.OutboxDispatcherTest',
 'api.messaging.outbound.OwnedOutboxDispatcherTest','api.security.LoginInboxServiceTest',
 'api.security.LoginReplayServiceTest','api.security.LogoutInboxServiceTest',
 'api.dispatch.JdbcRollbackAttachment330Test','api.dispatch.JdbcTransactionFatal329Test',
 'api.dispatch.JdbcTransactionBoundary329Test','api.error.TemporaryFailureGraph329Test',
 'api.error.ApiStartupGraph330Test','api.persistence.BorrowedJdbcFatal329Test',
 'api.security.AuthenticationJdbcBoundary329Test','api.dispatch.ApiReadinessFailureGraph330Test'}
WEB={'web.bootstrap.WebStartupGraph330Test','web.bootstrap.WebReadinessFailureGraph330Test'}


def correction():
    path=BASE/'PG6580-api-mapper-plan-v1/correction-v2.json'
    if sha(path)!='4c8995f83c0f44133a31be958e937f8cf5af7ee344c479ac580cb5e8ccb87482':
        raise ValueError('independent original-blob19 correction proof first')
    return json.loads(path.read_bytes())


def inventory():
    return profile.inventory({'api':API,'web':WEB},EXPECTED)


def mains():
    return {row['path'] for row in correction()['files']}


def targets():
    return {'api':[p.split('/src/main/java/dev/codex/schubert/nk/')[1][:-5] for p in sorted(mains())]}


def guard_source(source):
    proof=correction()
    for row in proof['files']:
        data=subprocess.check_output(['git','show',source+':'+row['path']],cwd=ROOT)
        import hashlib
        if hashlib.sha256(data).hexdigest()!=row['actualSha256']:
            raise ValueError('exact19 corrected Main bytes')
    changes=set(subprocess.check_output(['git','diff','--name-only',SOURCE,source,'--','src'],cwd=ROOT,text=True).splitlines())
    if changes!=mains()|{TEST}:raise ValueError('exact19 reviewed Main and one independent provider Test')
    if subprocess.check_output(['git','diff',RED_SOURCE,source,'--',':(glob)src/*/src/test/**'],cwd=ROOT):
        raise ValueError('all original independent Test bytes fixed')
    if subprocess.check_output(['git','diff',SOURCE,source,'--','pom.xml','.mvn','mvnw','program/characterization','tools/quality/static'],cwd=ROOT):
        raise ValueError('unchanged build/static/Current contracts')


def qualify_green():
    run=W/SLOT;source=json.loads((run/'begin.safe.json').read_bytes())['source']
    guard_source(source);cases,_=inventory()
    return qualify(source,run,cases,EXPECTED,mains(),
        BASE/'PG6574-jdbc-attachment-qualification-v1/manifest.json',
        'f8fb1042d4bd310987153659d7b1e51ca95a8d6337ae3df7d0e9c830efa8c5d0',
        W/'pg6574-jdbc-attachment-qualification-v1/manifest.safe.json',
        W/'pg6574-jdbc-attachment-qualification-v1/findings.safe.json',
        'pg6584-api-jdbc-domain-qualification-v1','PG6584-api-jdbc-domain-qualification-v1',
        expected_phase_exits=(0,0,0))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('phase',choices=('green','qualify-green'))
    if parser.parse_args().phase=='qualify-green':return qualify_green()
    cases,counts=inventory()
    return profile.execute(SLOT,guard_source,cases,counts,EXPECTED,targets())


if __name__=='__main__':raise SystemExit(main())
