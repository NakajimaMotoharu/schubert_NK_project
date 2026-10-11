# NK-BAT-001 PG1413 readiness raw byte・role型（実行前仕様）

Program MorningServiceReadiness.ready/ascii、ArtemisRoleReadinessClient.verify/verifyResponse。RD OPS009、SS341/SS321§10・SSC164、WBS-P018-07/P017-10主担当。Main769/PG1292不変更、試験二methodだけ追加。既Root/ADMIN/VM起動・配備・credential操作は行わない。

|Test ID|入力/操作/独立期待値|観点|
|---|---|---|
|PT-OPS-READY1413001|既public Io fixtureのstatusをraw byte0xffへ切替、ready()。IOException、status1回/IOrequest1回、socket/HTTP0|高bit byteをString US_ASCII replacementへ変換せず、未知kernel byteを検証前に拒否。既NUL/容量/UID/cap/HTTP/null観点は既6testで維持|
|PT-OPS-MQ1413002|SS321独立TABLEのnk.sync.requestはnk_web/nk_api/nk_opsの3role。配列長3を保ち各memberをnull/7/true/string/arrayへ置換、public verify()|固定redacted管理例外、role件数違いを原因に拒否したとは扱わない。正常live broker/各permission/unknown/null/redactionは既3testで維持|

予定strict selectedはMorningServiceReadinessTest7＋ArtemisRoleReadinessClientTest4=11/FES0、format先行済み、NullAway/SpotBugs0・Main全classbyte同1279を要求。既依存compile/Main資格はlive再認証して再build0・PT加点0、fixtureはprivate new-only tmpfs（隔離broker/NIOとowned stop、原本DB接続0）。新XMLだけを採取し旧targetはrecoverable保全する。expectedは独立SS role table/byte契約/停止後条件で、Production出力から生成0。

実command/source/run/時刻・環境/exit/XML/hash/coverage/関連BUGは081/publicmanifestへ実行後記録。未実行の時点で合格・全leaf・四100/正式/ITSTへ加点0。coverageは最新closing一件のみの当Main qualified inputへ追加し、同sessionunion0・classByteCRC0・独立XMLで検査する。
