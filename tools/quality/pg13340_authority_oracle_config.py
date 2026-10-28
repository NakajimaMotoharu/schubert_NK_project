"""Frozen seven Test authority dependencies; source correction never resolves unknown R09 acceptance ownership."""
from pg13336_state_oracle_trace import state_after
BASE_SOURCE = '703876e73d6ec1bd06229a8b9a119e66d8d99a30'
OLD_NORMAL = ('PG13330-state-oracle-v1','1d4bc617cab74a361cb8222a563e8080cc67857546d71525a49d224cb7b6ddb2')
PRIOR_TRACE = ('PG13336-state-oracle-v1','3b704ea0b52f06ed16019c8ef83999da8983cdf7e361a9275bf80ebb35278da2')
PREVIOUS_STATE = state_after
PREFIX = 'authority-oracle'
NORMAL_NUMBER = 13346
STATIC_NUMBER = 13348
TRACE_NUMBER = 13352
TRACE_POST_NUMBER = 13353
RECORD = 'evidence/01_PT/018_NK-OPS-001/2449_authority七箇所_独立oracle製造結果.md'
SS = ('documents/300_SS/310_アプリケーション/314_認証・認可・session・CSRF実装設計.md','ab7a1907d0861ca1b6d4181d674f98a73c13f8a4b897b86f655b5a30ce202a7b')
ROOT = 'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/'
SPECS = {
 ROOT+'SessionSecurityContextTest.java':dict(sha256='eb63e3a93db5cb2bc1229fff6ac40521d774a43acdbcf4ba172df855bb384eeb',count=2,owner='WBS-P015-02',methods={'auth':1,'assertIdentity':1}),
 ROOT+'SessionLoginHandlerTest.java':dict(sha256='8d366a07fc1c7a64379befd3af7e2344c9281bbd360fbe2919b71b375232a0c8',count=1,owner='WBS-P007-06',methods={'auth':1}),
 ROOT+'ApiSessionInvalidTest.java':dict(sha256='78bd572622a89cc73ed3b0250bb6cf2d69c21e77a697a21e06830d984648c491',count=1,owner='WBS-P015-06',methods={'setActor':1}),
 ROOT+'ErrorMvcTest.java':dict(sha256='9d8ede78b82dea660cdeb940ceca67b2d5d06e9177702035c4f3a23126befab4',count=1,owner='WBS-P016-24',methods={'set':1}),
 ROOT+'ScenarioControllerTest.java':dict(sha256='4b4940ba8202b7f52294ffad3859b6b37e46987309bdda6e900e46200b8e9101',count=1,owner='WBS-P016-07',methods={'setActor':1}),
 ROOT+'SessionAccessFailureTest.java':dict(sha256='82e37cfff94596f87fb6715ff2046b4d7c633631574513d105e34d6e8e131f69',count=1,owner='WBS-P015-02',methods={'setPrincipal':1}),
}
PATHS = {p:(v['sha256'],v['count'],v['owner']) for p,v in SPECS.items()}
FIELDS = {'USER':('EXPECTED_AUTHORITY_USER','ROLE_USER'),'ADMIN':('EXPECTED_AUTHORITY_ADMIN','ROLE_ADMIN')}
HELPER = 'expectedAuthorityFor'
PROTECTED = [ROOT+'SessionFormLoginTest.java',ROOT+'WebSecurityChainTest.java']
REMOVED_FINDING = 'PMD-09136'
assert len(SPECS) == 6 and sum(v['count'] for v in SPECS.values()) == 7 and len(FIELDS) == 2
