# NK-OPS-001 Root失敗世代の限定復旧 PT仕様

SSC147/PT-ROOTREC-TOOL-008～010: PG408 known app-auth failureだけを扱う隔離工具Pg409KnownAuthRecovery。008は固定Source/version/path/hash四値、承認canonical byte同値別instance/異version/異hash/malformed、正常非zero receipt保持/完全GC/部分GC/18field欠落/nullを独立literalで検証。009は真正private full18/watch/Broker AMQ229031 hashとRoot→同PID/caps0の事実、M/A/同署名BOM/専用DB/advisory/全162行14列/Backup/原本/完全kernelと旧PID消失を二読し、固定app2loginのみ配置、旧raw authとstartup10entryをroot専用にforce/readback保存する。010はProduction既存typed service/publication intent2件だけ退役、他byteとDB/Backupを不変確認、current INVALID/旧未完了を維持、historical close/新許可発行0。UNKNOWN/任意normal1/別Source/欠落相関は拒否して隔離。工具assertionはProduction件数へ加算0。BUG411413414、SSC146147/YKT328329。実command/後条件/hashは300へ、通常Root receipt30契約自体は緩和しない。

PG408/SSC145補足: ROOTREC006は実捕捉した正常30の完全18propertyと、その後の完全GC cold・全kernel終端を別証拠として認証する。GC単独/部分GC/別target/未知/生存PID/Jobは拒否し、過去30を現在GCから生成しない。ROOTREC007は旧DBの14列を独立fixtureで確認し、SUCCESS/WARNING/FAILED/SKIPPEDの終端を全て保全、前12列null/RUNNING/未知/別run/列不足・過多を拒否する。運用工具77assertionはProduction PTへ加算しない。receiptはstop前にprivate force/readback/sync保存し、今回だけは実Tool観測2026-10-01T08:47:05.933Zを元byte/hashのまま再保全する。観測日と保存日を分離し、raw InvocationやDB内容はGitへ保存しない。

対象: StartupPermitFiles/readRevoked、StartupLaunchFiles、BackupStartIntentFiles、InspectorUnitSnapshot、trusted配備 caller。RD OPS-009/SYS-002/004、UI251/253、SS342§4・343§6.15～17、SSC144。PG407、正式未認定。

- ROOTREC001: INVALID同Epochの旧permit全byteから独立SHA-256を算出、派生ISSUEDへverifyする。実currentをISSUED化せず、通常readIssuedが拒否を維持する。正常/root metadata/欠落/別binding/改変/null/IO/closeを区別する。
- ROOTREC002: Morning oneshot/no/Remainno、API/WEB simple/on-failure/Remainnoの独立18property literal。正常30のみ限定復旧資料、0/10/50/signal/timeout/GC/未知/別Invocation/start/end/PID/Jobを拒否する。従来worker receiptは変更しない。
- ROOTREC003: strict owner/launch/permit hash・boot/run/cutoff/activation/Epoch・親子Invocation/PID/start完全一致。publication intent許容は復旧専用相関readerだけ、通常Root namespace/permit受理は残留時拒否。
- ROOTREC004: 実保持inodeの既存空0600/root/tmpfs markerを採取し、同owner・gate前後・同inodeを再検証してservice→publication順retire。異inode/別adapter/null/割込/IO/close/追加namespaceでは成功0。unknownを期限経過だけで解除しない。
- ROOTREC005: VM旧失敗receipt stop前捕捉→M/A・旧Morning/固定8全kernelcold・旧PID消滅・専用DB/advisory/原本graph/全旧row不変・旧signed release/private保存/候補署名BOM→2intent退役→fresh INVALID配備→通常同run --resume。新Epoch/次Invocationへ旧intentを持ち越さず、旧失敗をdone化しない。

期待値は手書きbyte/18property/SS field・独立hash・DB全列後条件で作りProduction生成を使わない。host synthetic metadataを実root合格にしない。選択command/固定Source/環境/実結果/coverage/manifest hashは300へ記録、未実行・failed・skipped・flakyは算入0。全coverage100%/formal/業務ready/CHRは別未完。
