"""Frozen eight-Test PG-only literal scope; original canonical and runtime domains preserved."""
from pg13234_db_web_literal_trace import state_after

BASE_SOURCE = '1762d68747c3460afd90a03377858572dfc25931'
OLD_NORMAL = ('PG13228-db-web-literal-v1','3919599fe1f9798297a75b209802f656f3af603af3ed0df21f114e1dc0c39e74')
PRIOR_TRACE = ('PG13234-db-web-literal-v1','0787176b50c51f1dd2dd8722cbf8cf4771304b2d28fb95248b35b56a783ef402')
PATHS = {
    'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/application/scenario/ScenarioApplicationServiceTest.java':('8529ccd67722de03cc5e311f77f7f913c7360e1171cc39356d1301b2555d4e53', 21, 'WBS-P008-02'),
    'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/messaging/outbound/OutboxDispatcherTest.java':('062f789b78d1d691367542958f555526b8db0804243e026d2298092f2e6b5ee9', 19, 'WBS-P006-02'),
    'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/InboxMaintenanceBoundaryTest.java':('d12799cc0340fc9743688e887d249f5639d2bb7bde8fba842acbc761d31b8b0e', 19, 'WBS-P004-01'),
    'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/maintenance/NonAuthenticationInboxInspectorTest.java':('d8f482c436736742ca8d13060aced14a50125daa93db6591a8e49b3a3b29660c', 16, 'WBS-P004-04'),
    'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/ScenarioControllerTest.java':('6a6364f62363d72da0de17a6a4a21909c39f99c289d49d7af5a167859fc83f02', 16, 'WBS-P016-07'),
    'src/schubert-nk-batch/src/test/java/dev/codex/schubert/nk/batch/file/InspectorEnvironmentFilesTest.java':('3ef0653d44727e8eb8ef1551b77e9066fe82c3e294773594a959ded7ac730f7b', 16, 'WBS-P004-04'),
    'src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/security/LoginInboxServiceTest.java':('e7d09867b0400f921a56a323baf7333453fc2931efdac92b6d24920e70c0db51', 15, 'WBS-P007-04'),
    'src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/session/ApiSessionInvalidTest.java':('a49030f0a351f0d6d029d20c036af318a62f91de49b9be06b92f16257351e82e', 15, 'WBS-P015-06'),
}
PREFIX = 'business-delivery-literal'
ORIGINAL_NUMBER = 13238
PREFLIGHT_NUMBER = 13240
NORMAL_NUMBER = 13242
STATIC_NUMBER = 13244
POST_NUMBER = 13246
TRACE_NUMBER = 13248
TRACE_POST_NUMBER = 13249
BEFORE_RAW = 8143
BEFORE_TEST_RAW = 6641
BEFORE_CORRECTIONS = 1282
EXPECTED_CORRECTIONS = 137
RECORD = 'evidence/01_PT/018_NK-OPS-001/2434_業務配送保守八Test固定literal137件_製造静的確認結果.md'
PREVIOUS_STATE = state_after
