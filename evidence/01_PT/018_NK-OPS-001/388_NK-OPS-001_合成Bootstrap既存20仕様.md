# 同bab専用Bootstrap既存20・新合成source・通常退役仕様

Program NK-OPS-001/NK-ADM-001、BootstrapAdminMain/main/run/createAndCommit・Pg482BootstrapExisting/main、RD AUT001002/DAT009/MON004/OPS009/UI225226242、SS343§8.2 SSC188189196、QA047復旧範囲。常用API/Web permit/assemblyとは分離、Production source bab704707b8fd7e0dc7581c4489f0892236efe73/PG479/fresh3381PT508suiteのbyteを使う。

|Test ID|入力・操作/事前条件|独立期待値と根拠|
|---|---|---|
|BOOT482001|固定source、真正同runDONE/全app停止・新M/A/実DBexclusive/10Ref、全24DB/原本Backup/current/native/既17credential/旧retiredsource捕捉|各actor/全18/kernel二読。DB全column/private全tree後条件。app_users既存ADMIN1、未知/null/欠落/extra actorは拒否|
|BOOT482002|専用固定source2名が不存在時に新合成username/passwordをRoot400/new-onlyで発行|旧秘密を復帰しない、実account passwordは使わない。Unit/LoadCredential/argv/hardening/他全file不変更、秘密はguest Root私有だけ。directory timestamps以外と旧17物同byte/identity|
|BOOT482003|準備DBrollback/close正常後だけ一回start --no-block、同Unit普通UID999/zero caps/NoNewPrivs/kernel/新INVを捕捉|SSC189 shared保守TXをexclusiveで妨害しない。固定30s Unit期限、metadataRefは実行権限の代用ではない。既存ADMINなので正常exit20、row/hash/audit追加0、kernel/credential runtime全解放・正規terminal native capture|
|BOOT482004|Unit全終端後、新実DBexclusive/全条件再認証して合成sourceだけRoot私有へ回収|全24DB/原本Backup/旧native/旧retiredsource/全config不変。新Bootstrap exec単一1本だけ追加。新source2がsource namespace不存在、private before-imageで回収可能。新DB/Refchild0/A/M全部正常後のみcomplete|
|BOOT482005|同bab第10stream/current新INV・実独立counter再計数|agent sessionID BOOTSTRAP-actualINV-ordinary、開始/正常dumpが今回Unit期限内、同frozen六byte/NoMatch0。100%未達を合格にしない|

負値は固定command/source/UUID/metadata/foreign identity/null/欠落/row変異/同名source衝突/正常でない20/別nativeを拒否。期待値は上記literal、旧24DB全column capture、PID1/kernel実時刻、独立JaCoCo metadataから作り、Production methodでexpectedを作らない。工具fixtureはProduction PTに加算0。command/environment/source/branch/exit/coverage/BUG・hashは389結果とprivate manifestへ、credential・rawsession・DB・execはGit外。Unit/config変更不要の内部接続で上位仕様変更なし、IT/ST未完了。
