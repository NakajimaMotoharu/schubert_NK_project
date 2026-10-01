# NK-OPS-001 Root失敗世代の限定復旧 PT仕様

対象: StartupPermitFiles/readRevoked、StartupLaunchFiles、BackupStartIntentFiles、InspectorUnitSnapshot、trusted配備 caller。RD OPS-009/SYS-002/004、UI251/253、SS342§4・343§6.15～17、SSC144。PG407、正式未認定。

- ROOTREC001: INVALID同Epochの旧permit全byteから独立SHA-256を算出、派生ISSUEDへverifyする。実currentをISSUED化せず、通常readIssuedが拒否を維持する。正常/root metadata/欠落/別binding/改変/null/IO/closeを区別する。
- ROOTREC002: Morning oneshot/no/Remainno、API/WEB simple/on-failure/Remainnoの独立18property literal。正常30のみ限定復旧資料、0/10/50/signal/timeout/GC/未知/別Invocation/start/end/PID/Jobを拒否する。従来worker receiptは変更しない。
- ROOTREC003: strict owner/launch/permit hash・boot/run/cutoff/activation/Epoch・親子Invocation/PID/start完全一致。publication intent許容は復旧専用相関readerだけ、通常Root namespace/permit受理は残留時拒否。
- ROOTREC004: 実保持inodeの既存空0600/root/tmpfs markerを採取し、同owner・gate前後・同inodeを再検証してservice→publication順retire。異inode/別adapter/null/割込/IO/close/追加namespaceでは成功0。unknownを期限経過だけで解除しない。
- ROOTREC005: VM旧失敗receipt stop前捕捉→M/A・旧Morning/固定8全kernelcold・旧PID消滅・専用DB/advisory/原本graph/全旧row不変・旧signed release/private保存/候補署名BOM→2intent退役→fresh INVALID配備→通常同run --resume。新Epoch/次Invocationへ旧intentを持ち越さず、旧失敗をdone化しない。

期待値は手書きbyte/18property/SS field・独立hash・DB全列後条件で作りProduction生成を使わない。host synthetic metadataを実root合格にしない。選択command/固定Source/環境/実結果/coverage/manifest hashは300へ記録、未実行・failed・skipped・flakyは算入0。全coverage100%/formal/業務ready/CHRは別未完。
