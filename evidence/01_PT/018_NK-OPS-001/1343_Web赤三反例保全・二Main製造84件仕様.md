# Web赤三反例保全・二Main製造／84件仕様

## 元PG6294真正結果

元tool62624、Test-only source `1e98c9daffb1a6db6c9fae290841e89f0ff10cbe`（全Production Main b423同byte）、2026-10-21T01:24:36.904620Z～01:26:10.298931Z、真正1/phase[0,1]/Maven1。実26件/7suite/F3E0S0、後続batch2件/2suiteはnot-run、全28合格にはしない。先行全六format0、終了前protocol/storage/bootstrap/apiの静的0、web/batchの後続静的・新target coverageは未測定。旧targetの0/0 placeholderを100%へ変換しない。

私有PG379/pg6294-web-send-red-v1：begin SHA256 `8dfe520347721837addb428af83df105cb7a56196867584c787b40c47de1cbd2`、archive `890828431312d5d4bb415b5183494834afe8491762b8d7f0a4d5e4b365160aa5`、manifest `eb974557b51df5b270da10f72cd827796ca94c776d12fe9f01c901d090ddae07`。原command/環境/branch/source/全XML/input/result/logを保持、raw credential/DB/鍵の公開0。

|Test ID|最初の独立期待|実際|原XML SHA256|
|---|---|---|---|
|WEB321001|cleanup LinkageError同一性|primary IllegalStateException|dc9dd4b94827b8e344b216d85cce0344d9cfc1dadb06cf96007377a9ac0bacf5|
|WEB321002|cleanup LinkageError同一性|WebLogSendException（固定lifecycle failure）|48d965e420cbc34dc364c82886ea58f53767960abb984de3c565cf837245844f|
|WEB321003|同じprimary AssertionError|WebLogSendException（TWR self-suppressionからの置換）|48d965e420cbc34dc364c82886ea58f53767960abb984de3c565cf837245844f|

三methodとも先頭反例で失敗した。以降のmatrix入力は未到達、他23JUnitの成功や旧全4040へ加算しない。1569/1570は修正前起票済で当三反例を追記する。

## PG-D475／二Mainの製造（未検証）

ArtemisRequestSender.closeAfterFailureに、nonfatal primary＋close ErrorだけそのErrorを優先する分岐を追加。他primary無し/元Error/self guard・直接checked JMS契約は維持。WebLogMessageSenderはTWRのgenerated self-suppressionを避ける最小manual primary/try/finallyへ変更し、同class内private close helperで同順位・identityを保持する。復号wireの最外finally wipe/未取得close0、元stage/commit/rollback/duplicate graph/TTL/MessageID/property・typed固定redactionは不変更。新class/module/設定/権限なし。

正規format元31563真正0（2026-10-21T10:28:18+09:00）、src差分は二Mainだけ、独立三Test/他全Test/Current/gatesは原1e98と全同byte。未compile/未実行であり修正済み合格とはしない。JmsRequestReplyClientはsend/waitのfinallyでcorrelation cancelとpermit releaseを保持し、Errorを一般Exceptionへcatchしない既構造を確認、ordinary dispatcher/workerと共に関連再試験する。実Root/native cleanupの証明には使わない。

## PG6296／6298（まだ未実行）

当独立3を含むRequest9＋Log7、既定12、既OutboxFailure6/Dispatcher19/Owned5/WebLogDispatcher9、JmsRequestReplyClient8、WebLogReplayWorker9を実source宣言から一意に列挙し、**84件/15suite** を一回実行する。既正常broker/DB後条件・duplicate graph/同fatal順位・worker/caller所有と再送の非回帰を含む。数式は選択内訳であって成功の算術加算ではない。通常自己所有tempPG/in-process broker/HTTP・有限worker fixtureのみ、実PGPT VM/current/Root/cohort等操作0。compile/format/型null/Test警告/SpotBugsの全六gateを維持する。

保存pushclean後、所定PYTHONPATHで`python3 -B tools/quality/pg6296_web_send_green.py`を新only slot pg6296-web-send-selected-v1へ一回。元三失敗・原source/Test不変更・二Mainだけの差分を入口で検査、真正終端まで全Main/Test/gates固定。0後`pg6298_web_send_qualification.py`が当原全XML/六Jar/8511667/二owner差分/実coverageとrawPMD/CSを独立検査する。旧source4040/51/nativeを新sourceへ移植せず、必要同source全体・静的適用性/trace/実coverage/残PGPTへ続ける。新定義2件/pyflakes0、実84やcoverage100はまだ未認定。

計測：1531は元1530のsource略記を原行保持でfull1e98へ追記補正し、原赤結果と現二Main未検証を区別。1532はb423/原4040/artifact/traceの限定技術作業群END（K01.01 leaf/PGPT完了ではない）、元開始見積.5/1.5/4を維持する。Web追加発見の群1529開始.5/2/6は別枠、原-v4残/親群/実費と混同0。freshused35/残65/reset1793082865/secondary不明、usage7ba793e7/N-T専有費工数null、reset秒の観測差から専有費やtokenへ換算しない。

正式1964/53・17-190・QA051final/PTALT不明代替0、実VM/current/Root/cohort/intent/permit HOLD・全保全物維持。通常三反例/PG/commit/限定成功で停止しない。
