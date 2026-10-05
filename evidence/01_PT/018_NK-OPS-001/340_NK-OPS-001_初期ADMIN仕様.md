# 初期ADMIN 単体テスト仕様

PG465/NK-ADM-001 BootstrapAdminService.create/audit/require及び後続専用oneshot/credential owner。関連AUT001002/DAT009/MON004/OPS009/UI225226242/SS314331332343§8.2/351352/SSC188。既存UserCommandServiceの認証済ADMIN入口は空DBへ流用しない。

|Test ID|fixture/入力・操作|独立期待値|
|---|---|---|
|PT-ADM-BOOT001|隔離PG18/実Flyway/限定schubert_app TX、空DB、ASCII NFC/trim username/password境界|1ADMIN ACTIVE/version0/初期NULL actor/同UTC日時、独立JCA PBKDF2 salt/hash照合、USER_CREATED ACTION SECURITY2行/actorNULL/固定safe details、配列zero|
|PT-ADM-BOOT002|既存ADMIN/USER、ACTIVE/DISABLED、再実行、invalid creation password|ALREADY_EXISTS/後続exit20、全User/ログbyte不変、hash化せず配列zero|
|PT-ADM-BOOT003|空DB、username非ASCII/空/65byte/password11,129cp/257byte/同username/control/null|契約拒否、rollback後User/ログ0、秘密を例外に含めず配列zero|
|PT-ADM-BOOT004|100bootstrap並行・別connection commit、非協調INSERTが先にtable lockを取得|全体1件のみ作成、他99既存、非協調既存でも追加0、各lock/TX資源は正常返却|
|PT-ADM-BOOT005|audit SECURITYのDB triggerが故障、作成後rollback、無権限・autoCommit/readOnly/非READCOMMITTED|commit成功を宣言せず、rollback後User/監査0、DB/TX所有をcallerから奪わない|
|PT-ADM-BOOT006|SQL projectionの欠落/null/複数/未知ID/executeUpdate異常及び資源close故障|SQLException failclosed、null契約境界/全例外counter、passwordzero、下流正常化0|
|PT-ADM-BOOT007|専用Unit・systemd credentials/schema/同owner/通常返却・既存時20|実Unit確認・秘密非表示・固定role/grant・DB原本/Backup保全、未実行を合格化0|
|PT-ADM-BOOT008|別session実Login/変更/ADMIN検査→bootstrap credential退役|現在API/Webによる真正成功、固定初期passwordなし、再送重複作成0、別source結果流用0|

expectedはDDL/固定SQL後条件と独立JCA/手書き列から算出。Production encode/matchesでexpectedを生成しない。実行環境/command/source/exit/XML/coverage・BUG・hashは341へ記載。coverage全4counter/native・fresh全回帰・秘密/trace未確認なら正式未認定、TDD未実装はBUG対象外。

## 初期ADMIN接続の正常DONE配備依存（SSC190、工具assertionsはProductionPTへ算入0）

|Test ID|入力・操作/独立期待値|
|---|---|
|PT-ADM-DEPLOY001|固定CLI/正常DONE時刻両境界/未完・WARNING・別runactivation・nullをliteralで検査、正常全値だけ受入|
|PT-ADM-DEPLOY002|歴史28＋現4＋epochの33集合・全33欠落/foreign/intent/余剰を拒否、旧rawrecordを権限へ流用0|
|PT-ADM-DEPLOY003|手書き8Unit逆順（Caddy,Web,API,Cleanup,Inspector,Expiry,Backup,Artemis）と全8fault位置、faultの同一性/後続発行0。各stop直前は固定F18/同PIDInvocationtickを再認証、UNKNOWN保持|
|PT-ADM-DEPLOY004|実VM verify、同M/A/DB/currentboot/signedoldnew/5INFO/ordinarycaps0/socket/TLS/current親journal jobdone/正常DONE/DB331/Backup20/原本/Transfer/33byte。全scope通常返却、startpermitDDL0、停止を受入したと読み替え0|
|PT-ADM-DEPLOY005|実VM一回activate、同所有Unit真正正常停止/kernel/旧PID消失、新INVALIDだけ、raw32byte/DB全値/原本DONE/Backup20/Transfer不変、signedcurrent切替/新bootstrapUnit staticinactive、全scope正常返却後のみ成功。発見故障は修正前BUG、未実行/UNKNOWNを成功へ算入0|
