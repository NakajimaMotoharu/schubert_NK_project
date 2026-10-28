"""Frozen existing two-Test oracle correction; no target Test or old G03 job authorization."""
from pg13320_null_fixture_review_history import state_after
BASE_SOURCE = '81a1b0c32be8167c07320e6bfaf469bcd44eb7bd'
OLD_NORMAL = ('PG13306-web-business-literal-v2-v1','54547059dfcc03323666371126747e3503b35373bae18cc6b49de23d13854cea')
PRIOR_TRACE = ('PG13312-web-business-literal-v2-v1','7443c34223aeec8eb18fdf870c68bf1dccd170d5c31f226c997d12e6ad6faaaa')
PREVIOUS_STATE = state_after
PREFIX = 'state-oracle'
NORMAL_NUMBER = 13330
STATIC_NUMBER = 13332
TRACE_NUMBER = 13336
TRACE_POST_NUMBER = 13337
RECORD = 'evidence/01_PT/018_NK-OPS-001/2447_質問通知state八箇所_独立oracle製造結果.md'
UI = ('documents/200_UI/230_インターフェース/236_管理・質問・通知電文仕様.md','0468f20da240ed61e056084f80e88f3b3f5d60b3afb70f23710a8320c5c653c9')
SPECS = {
 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/QuestionControllerTest.java':dict(sha256='56d185a9df42ba845e55817417533626f4d09ddaabe95c2aa98fb8999fc61672',count=6,owner='WBS-P016-18',enum='AnswerState',helper='expectedQuestionStateWire',
     fields={'ANSWERED':'FIXTURE_ANSWERED_6CA66E97','UNANSWERED':'FIXTURE_UNANSWERED_8B420ADF','ERROR':'FIXTURE_ERROR_F717E7D8'},methods={'qry006DetailWholeWireAndDisplay':2,'qry008MvcEscapeRolesStatesAndMethods':3,'qry011FactoryControllerNullAndIntegrity':1}),
 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/NotificationControllerTest.java':dict(sha256='9a202dd561060fab3d056026da13317e0de00b9f539b1387fd5a6af522bf9d42',count=2,owner='WBS-P016-21',enum='NotificationState',helper='expectedNotificationStateWire',
     fields={'RECEIVED':'FIXTURE_RECEIVED_35302D54','PROCESSING':'FIXTURE_PROCESSING_01F94682','COMPLETED':'FIXTURE_COMPLETED_BA0AE16A','ERROR':'FIXTURE_ERROR_F717E7D8','CANCELLED':'FIXTURE_CANCELLED_E01A549A'},methods={'ntf007AllStatesTypesSummaryAndImmutableDisplay':1,'detail002StateDatesDeletedAndEmptyAnswerProjection':1}),
}
PATHS = {p:(v['sha256'],v['count'],v['owner']) for p,v in SPECS.items()}
assert len(PATHS) == 2 and sum(v['count'] for v in SPECS.values()) == sum(len(v['fields']) for v in SPECS.values()) == 8
