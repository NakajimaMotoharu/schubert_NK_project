# PG564 Log・HTTP session実独立結果

2026-10-08 15:17JST、工具固定source23a0162ec、Production969/PG548/schema028、branch dev-foundation。仕様465/Test001～006、hostliteral4test成功・Pyflakes0、実collector終了コード0、私有stderr空SHAe3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855。

|受入成果|今回新確認|未認定範囲|
|---|---|---|
|Log/outbox/local|114Message ID一意join・114暗号AES-GCM/AAD・2336byte全header/data/Details・local/DB同値、匿名GET/login200INFO、全SENT/leaseなし/attempt0|新停止・再送注入なし、QA051/CHR-L01最終PASSなし|
|HTTP session|114全独立復号・匿名JSON version2/CSRF標準64hex/空operationTokens、AAD/8h idle/row時刻、nonce/hash一意|rawCookie一対一join未採取、認証session全品質を本匿名結果へ拡大0|
|保全|当boot/currentrelease・全24現在rowと十Unit全値を前後二読、retired runtimeなし、start/stop/reload/SQLwrite0|既旧UNKNOWN143・BUG850旧stdout原byte未回復は不変更|

証跡private W=/home/mini/codex/project1/work/pgpt-runs/PG379/pg564-log-session-capture-v1.safe.json、SHA3eb577c4f03683c00e39d7de416c278e628298b6aa3e147ac269ec8f75efe4e4。guest Root `/var/lib/pgpt-s1-preservation/pg564-independent-log-session-v1/result.safe.json`、journal SHA05be178125ecd9dc0a2e02ac2cbb5ad60913ad32ef498bebf5eb789bae0cc84c、sealed beforeb9a70c…/after23263d…。独立oracleSHA7ef66fbee46258540f6760354fe59dbfc03bb7028c5f8dd33152030cb7fe47f5。commandは465に一致。Ubuntu26.04/PG18.6/JDK25.0.4、Pythoncryptography AESGCM、鍵/CSRF/plaintext/export0。

原始eventのresponseBytesはwire/DB/local一致のみ。client受信bodyとの実byte比較はこの保存runで未採取。全scope同source正式品質・currentBootstrap native・残faultmatrix/coverage・CHR・引継ぎは残る。Java PT件数加点0/正式PT-WEB-20260925-24 1964PT/53scope不変更、WBS ACCEPTED0・工数率null。本結果は今回114件の実後条件の新成果であり、未受入を成功に算入しない。
