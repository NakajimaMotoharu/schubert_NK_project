# API service/Outbox metadata接続・PG/PT仕様

2026-10-25/主WBS-P018-09/C07 shared追加予算0、PG-D630/NK-OPS-001/RD171/UI252/SS311332342351。開始HEADb628e82a2/製品f690fa6be、fresh51残49/reset1793382075、開始2/5/9pp cap10固定。後続索引1671/1721と現API context/callerを確認。既Outbox SQL/collectorは製造・普通試験済みで再実装しない。実readは独立RO transaction/READ_COMMITTED/timeout1秒を要求するため、dispatchのRW connectionを流用しない。

この群は非resource API service bindingだけを製造する。既DbPool binding＋Outbox rows/age recorderを同registryへ登録・strong保持し、ownerのrefreshでは既所有の不変Snapshot/Optionalを一度借用する。SQL/connection/worker/Clock/SDK owner操作は追加せず、source supplierはI/O/owner再入をしない契約。default factoryはOptional.emptyなので実source未供給を六gauge NaNで明示し0を捏造しない。ApiProcessMainは既scope/開始停止順を保持したfactory/type供給だけを差替える。実RO source/有限sampler・quiescence/親配置/nativeは別依存/未受入であり、今回それらの稼働を推定しない。

snapshot取得のnull/Runtime/Error又は先行pool取得失敗はfinallyでrows/age/lastをmissingへ戻し同primaryを維持。STDは全supplier未読、factoryはresource-freeでowner捕捉後の明示initialize。snapshot公開は不変valueのみ、registry/collector/Valve等のmutable getterを作らない。health/readiness決定権・外部HTTP/業務仕様・認証/電文/SQL/再送契約は変えない。

APISERVICE001～016新16と既ApiMetricHttpHandlerTestに新APIMHTTP022一件を追加。既21を必要回帰として計38/2suite、新Java ID17/新Main1予定。constructor/factory null・不正mode、supplier未読/一度取得、正常/空/未供給NaN/更新、pool/provider Runtime/Error/nullでのmissing・同primary、owner close後未読、HTTP明示200/UTF8長/Content-Type/no-store/一回closeを独立literalのSS名/label/値で確認する。Count/Age fixtureは手書き3/5/7・2/4/6秒、expectedをproductionで生成しない。既pool fixtureはtyped getterだけでDB/Pool/JMX controls0・outer Testはcompile-only/未実行をPASSにしない。

9028正常六compile→9030選択38→9032新binding/handlerの同source scoped四100/NPE/static→9034全物理/既byte/保持Main business code・owner/trace→1853結果/公開scan/保存push。sourceを先に固定し別sourceへ成功を流用しない。API callerのactual start/close/全class/nativeはHOLD/null、既static raw二件は当source/原根拠との結合が必要で免除しない。全C07/451/正式1964-53/原190新受入0/QA051final/工数null/元-v4-v5/全actualHOLD維持、通常区切り停止なし。
