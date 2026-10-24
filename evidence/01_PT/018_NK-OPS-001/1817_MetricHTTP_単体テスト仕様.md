# API/Web metric HTTP境界 単体テスト仕様
NK-OPS-001/RD171 MON010～013/UI252/SS311342351/PG-D618。主WBS-P018-09/C07追加費0、group2047、fresh43/残57/reset1793382075、開始見積2/4/8pp・cap10。
ApiMetricHttpHandler/WebMetricHttpHandler新2Main/各16Unit。1814/8734既manager応答と1815-16contextを基点に、固定GET/rawpath/UTF8/byte長/no-store/exchange closeのHTTP境界を製造する。管理server/Root/default socket/実サービスは変更も実行もしない。借用contextを初期化・closeせず、readinessを一回だけ取得して全render成功後にheaders/bodyを送る。失敗は既respond同様callerへ伝播し、200やready-only fallbackを捏造しない。新業務仕様/権限/port/data-sourceなし。

APIMHTTP001..016/WEBMHTTP001..016、計32/2。class ctor/handle全line-method-class-branch対象。fixtureはmemory HttpExchangeとownSDKのみ、socket/server/VM/DB/外部processアクセス0。DEBUGは実own標準SDK、Gauge7.5→9.5固定literal、STDはsetup未読。expectedは手書きready/header/status/text、UTF8独立byte計算、例外identity、独立calls/closed状態、actual production renderをexpected生成に使用しない。

|ID末尾|入力/操作|独立期待|
|---|---|---|
|001|STD ready true|GET200/ready1、GET後context借用継続/ready一回|
|002|STD false|GET200/ready0（service health200へ偽装せずmetric応答）|
|003|DEBUG実registry/標準/metadata更新|固定custom7.5→9.5/標準JVMtext/byte長/owner未close|
|004|POST HEAD get OPTIONS|405/{}・未初期化contextやreadiness未読|
|005|末尾slash/encodedpath/info|404/{}・rawpath厳密/詳細未読|
|006|queryあり固定rawpath|200/固定readyのみ・queryをlabelへ出さない|
|007|null ctor二入力/exchange|invariantでNPE拒否、正常扱い0|
|008|未初期化context|成功headers/body0/close・後にcaller init可能|
|009|closedcontext|失敗・成功headers/body0|
|010|ready Runtime|元identity/close/headers0/context保持|
|011|ready Error|元identity/close/headers0/context保持|
|012|headers IOException|元identity/close/body0/context保持|
|013|body IOException|元identity/close/owner保持、再初期化0|
|014|未知pathへのPOST|method優先405・readiness未読|
|015|同handler連続ready変化|各一回/1→0・値cacheなし|
|016|既存二header|setで一値へ置換・借用context保持|

source固定後8752正常six（製品PT0）→8754新32/2→8756当2四100/static/CRC-session/negative→8758全1832/旧1830-原1669不変/owner219/architecture/資源取得なし→1818/hash/scan/保存push。Source/command/environment/date/branch/exit/coverage/BUG/pathsは各manifestと結果へ。初回未実装不合格はTDD、実装済み違反は修正前915/916起票。着手時32 UNRUN、旧52/4222確認再演0/合算0/除外0。既供給観測/鮮度/全catalog/endpoint配線/actual native/CHR/whole451は未受入。正式1964/53・原190新受入0・工数null・QA051final/PTALT0/HOLD/元見積/v4/v5/原本等を維持。小区切り停止なし。
