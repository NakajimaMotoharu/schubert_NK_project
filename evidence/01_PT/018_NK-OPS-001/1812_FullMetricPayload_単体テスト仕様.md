# ready/custom/標準text 全payload接続 PG/PT

NK-OPS-001/RD171 MON010～013/UI252/SS311342351/PG-D616、主P018-09/C07費追加0。group2041開始fresh41残59/reset1793382075/2-4-8pp/cap10、着手前431/1799/1800-01/1809/1811/現sourceを照合しfull接続未実装を確認。API/Web既CustomMetricPayloadへ4引数render overloadだけ追加、新Main0/変更Main2/POM差0。旧3引数API・ready prefix/入力検証/借用・mode診断は互換維持する。

新overloadは同role StandardMetricSourceを借用し、STDは既ready-only結果だけ/詳細source未読、DEBUGは旧ready+approved custom textを先に形成してから公式標準textを付加する。標準owner/text null・custom/標準供給/formatter失敗は例外を伝播してpartial text成功やready-only fallbackにしない。自動bind/close/retry/health計算/HTTP操作なし、二観測は全体transaction/snapshotを保証しない。公開call側が両sourceを保持しGC等の明示cleanupを行う。

Program ApiCustomMetricPayload/WebCustomMetricPayload、4引数render/新固定STANDARD_MODE、旧constructor/3引数renderとの接続。新APIFULL001～012/WEBFULL001～012各12件、既APIPAY/WEBPAY各13件は変更した同Mainの既存byte互換を検証する必要回帰として実行する。計50/2、新規成果24/必要回帰26、旧成功の確認だけの再演/新規計上ではない。

|末尾ID|事前fixture/操作|独立期待と根拠|
|---|---|---|
|001|STD・未初期化/closed標準owner・ready1/0、取得時失敗supplier|legacy固定ready byteのみ/custom factory0/標準factory0|
|002|固定custom2family＋固定標準fixtureのready0全量golden、別own JVM公式SDKのready1|ready→custom→standardのliteral順、default公式CPU countと独立Runtime値・JVM名、借用source未close|
|003|unbound/closed標準owner＋DEBUG custom|標準不可の明示拒否/partial text成功0・custom一回/owner保持|
|004|null標準owner/null source/null・未知mode|境界拒否と各旧mode診断、provider/標準scrape未読|
|005|custom supplier Runtime・標準にも故障設定|元custom Runtime identity、標準呼出0|
|006|custom supplier Error・標準にも故障設定|元custom Error identity、標準呼出0|
|007|custom formatter getMeters故障|元例外identity/標準呼出0/借用close0|
|008|custom正常後の標準Runtime|元標準identity/標準一回・自動close/ready fallback0|
|009|custom正常後の標準Error|元Error identity/成功textへ正規化0|
|010|標準SDK portが契約違反null textを返す|NPE境界拒否、文字列null混入の成功0|
|011|共有標準ownerとimmutable customで64並行render|各固定prefix/custom/CPU独立値、重複namespace/close0、有限join|
|012|custom supplierをlatchで保留中にcallerが標準をclose|続行後標準不可で失敗、partial成功0/custom借用保持、owned workerだけ有限join|

固定READY/CUSTOM/STANDARD goldenは手書きliteral、公式CPU値は同JVM Runtimeから独立取得、production render/scrapeでexpectedを生成しない。GC/弱参照Gauge fixtureをcallerが保持しreachabilityFence、実Clock/HTTP/DB/VM等は操作しない。新12ではfactory port/own JVM標準SDKを使い、旧26の期待・Test IDは変更しない。

source固定後8722 normal六module→8724 actual50/2→8726当変更2の全line/method/class/branch100・全static・七metadata反例→8728全1828物理/変更2以外旧1826同byte/原1669/全213source-owner・五edge/固定二String field/借用→1813/scan/commit-push。全command/環境/日時/branch/source/exit/入力期待実際/coverage/BUG/hashはmanifest/resultへ。failed/skipped/notrunをPASSへ加算0/旧exec union0/抑制・除外0。障害修正前915/916。

着手時新24/必要26 UNRUN。正式1964-53/原190新受入0/工数null/QA051final/PTALT0/whole451/CHR/native/実endpoint/起動/VM/Root/拒否対象等HOLD不変更。原本/鍵/stash/Currentbaseline保持、通常小区切りでは停止しない。
