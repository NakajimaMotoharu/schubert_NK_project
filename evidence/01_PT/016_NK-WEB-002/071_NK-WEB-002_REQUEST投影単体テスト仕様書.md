# REQUEST投影単体テスト仕様書

SSC173/PG-D355追補：responseBytesはorigin charset変換後のsuccessful content write、headers/transfer chunk framing/Servlet char混在/Caddy後段/clientACK保証は対象外。独立実UTF8本文・HEAD0・ASYNC固定6で確認し、production counterからexpectedを算出しない。BUG573～586/YKT414～418の再試験も同Sourceで実施。新対象はlogging.WebRequestTrace/Scope、WebRequestLogProducer、HttpRequestLoggingValve、WebRequestRouteInterceptor、config.RequestLogMvcConfiguration、既存bootstrap.WebHttpServer/security Context・Caddy・ClosedServlet・LoginSuccess hooks。class/method単位Test IDは下記3新suiteと既存REQ015 integrationへ対応、署名・command/source/全4counter/manifest hashは072に確定する。

| suite/method群 | Test ID | 独立oracle |
|---|---|---|
| WebRequestTraceTest req004/006/007/008 | REQ004/006/007/008 | UI/actual24 mapping＋static2のfixed inventory、literal UUID/role、cross-request/null/unknown・100並行/nested/誤thread・framework redaction |
| WebRequestLogProducerTest req005/007/009/010/011/012/013/014 | REQ005/007/009～014 | literal JSON/手書き全2336/JCE-AAD、DDL後条件、独立SQL/runtime/fatal/同fatal/close fault、numeric/IPv4IPv6 boundary |
| HttpRequestLoggingValveTest req001/002/003/004/005/006/008/016 | REQ001～006/008/016 | actualTomcat11.0.25 HTTP応答値・独立UTF8 body/N0/HEAD/ASYNC/terminal一回、malformed/override拒否/lexical解除/外側資源所有 |
| WebApiLogReplayIntegrationTest.req015NewProducerUsesExistingWorkerRetryBrokerAndApiUk | REQ012/015 | 新producer→実Web18 technical row→既存worker/Artemis→API UK、同期queue0/初回故障/固定due再送/二配送row1・明示eventUUID SQL |

2026-10-03、NK-WEB-002/NK-MSG-002、MON001～013/FUN008/AUT/MQ、UI235 §12/252 §2/242、SS312 §11/351 §3.4/324/352/342、SSC172/PG-D354。対象HttpRequestLoggingValve・request-scoped trace/producerのconstructor/invoke/log/format/投影、既存WebLogPayloadCodec/Repository/Dispatcher/Replay/API ingestとの実接続。詳細class/methodと実command/対象source・hashは072へ確定時に記録する。

| Test ID | 条件・入力・操作 | 独立期待値と算出根拠 |
|---|---|---|
| PT-REQ-LOG001 | 実Tomcat11.0.25 normal GET/HEAD・UTF8 text/body | clientの明示HTTP status/header/body、terminal callback1回・final byte、HEAD body0、status/elapsed確定後 |
| PT-REQ-LOG002 | 同実HTTP redirect/sendError/throw/ERROR再dispatch | 最終302/400/403/503/500、元request ID/event1・query secret0・前段200で誤確定0 |
| PT-REQ-LOG003 | ASYNC二cycle/complete/timeout/error/切断 | 実終端のstatus/byte/count1、未終了callbackを成功化0、dispatch間trace同identity・終了scope leak0 |
| PT-REQ-LOG004 | HTTP method/route正常・未知/encoded/query/fragment/秘密canary | registered pattern allowlist又は固定/**、raw URI/query/header/body/cookie/context/token/password採用0 |
| PT-REQ-LOG005 | native AccessLog null/request・response欠落/未検証proxy | safe local UNKNOWN/固定alert、wire必須trusted IP/status捏造0、例外原文/正常化NPE0 |
| PT-REQ-LOG006 | server UUID/verified Caddy IPv4IPv6・header spoof | 既存Caddy監査と同requestID、pretrust identity≠transport grant、IPは検証済literalのみ |
| PT-REQ-LOG007 | Login成功/失敗・protected USERADMIN・失効 | 検証済username/roleのみ安全snapshot、NFC/control除外、Login失敗attempted username0・principal/context保存0 |
| PT-REQ-LOG008 | 100並行/nested/Async・非HTTP worker UUID | request間混線0/lexical scope終了解除、first MQのみ・後続probe不変、MQなしcorrelation=eventID |
| PT-REQ-LOG009 | monotonic ns/unknown0/負・N9/N12境界とbody bytes | 手計算ns/1_000_000、wire999999999/local999999999999上限・truncated印、無根拠成功補正0 |
| PT-REQ-LOG010 | 固定Clock/UUID/HTTP・独立JSON/2336byte vector | UI232 header256の手書きE/I/context全space、UI235 data2080下記offset、local/outbox同event/correlation/明示値 |
| PT-REQ-LOG011 | 既存AES暗号化/復号・改変/鍵寿命 | 固定synthetic JCE-GCM/AAD独立復号・rawwireと全byte一致、既存NKENC1/用途鍵/retained owner不変 |
| PT-REQ-LOG012 | 実Web technical DB INSERT/duplicate/transaction | encrypted row1/PENDING/同UUID UK不変、businessDB0・HTTP thread JMS0、短TX確定後worker send/ingest UK |
| PT-REQ-LOG013 | DB get/INSERT/commit/rollback/close不明・codec故障 | local PENDING→同event FAILED補足/固定alert、HTTP status/body/header不変、秘密/provider文面0・成功化0 |
| PT-REQ-LOG014 | local sink故障・unknown/null factory/不変snapshot | local成功としない・owner固定terminal、request business結果不変更、caller資源二重close0/owned消去 |
| PT-REQ-LOG015 | 実既存outbox worker/JMS reply/ingest再送/応答喪失 | 元UUID/DB UK、同Source既存正本fixture/SQL後条件、producerの同期send0・retryは既存dispatcher |
| PT-REQ-LOG016 | HTTP drain/worker join/replies/DB-JMS-key/部分ready拒否 | 完全owner逆順close/故障条件、fullbusiness未組立READY不可、native/source採取とformalは別 |

独立wire data zero-based offsetはUI235から：timestamp0/17、type17/16、level33/8、action41/64、message105/512、requestId617/36、method653/8、path661/256、status917/3、elapsed920/9、remote929/45、username974/64、role1038/5、details1043/1024、Reserved2067/13。総2336は手書きheader256+data2080、padding全space/固定vector、expectedへProduction encode/format/JSON生成を呼ばない。JCE/AAD計算も独立fixtureのみ。実response値とSQL後条件・synthetic secret canaryを明示し、実credential/session/token/password/key/master/dumpを証跡へ保存しない。

null/欠落/empty/未知/異常/例外/境界/並行/再送・line method class branch100/static0/独立oracle/同Source全scope条件を維持。失敗/skip/flaky/not-runは合格0、nativeや正式53scopeは実証前未受入。PG441 safe/frozen成功を新Sourceへ流用しない。
