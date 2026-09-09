# NK-DAT-001 検査DB credential・接続 実行結果

047/PT-DB-INBOX-193～208、SS343 §6.6/342/352、SSC-049/PG-D-142。正式PT-WEB-20260909-36/source1dc0b57dae258495f2198f3e348c150030b2e413、2026-09-09 17:46:15～17:53:11 JST、dev-foundation、exit0。新16件全PASS、全体1027件（Protocol80/Storage42/API594/Web241/Batch29/CHR41）成功、failed/error/skipped0。6 Java moduleのline/method/class/branch100%、Production5 moduleのNullAway/Enforcer/Spotless/SpotBugs PASS。全31scope/10collectorの同run/source/branch/hash/参照と017/019の10負canaryも成功。evidence/inspector-database/manifest.json SHA-256 `f34e56a41dbea484def980992b95ee83db2282a32a78184f16e3f8066abb3fb2`、全体manifest SHA-256 `80cd4b20c5d8a7bcb8074548c933ebc39111ef95df1a4480ae0ae633ce14ee57`。

InspectorDbCredential class1/method6/line36/branch28、InspectorDatabaseConnections class1/method8/line51/branch28、各missed0。共有access/loader/nestedも同manifestの全counterでmissed0。実PGのSCRAM正誤・専用role/42501・100fresh接続・open/close排他、独立暗号/SQL後条件によるrollback2/0→最終1/1（検査2/削除1/保護1）と再開を確認。BUG130～133/YKT103～104を本runで再試験完了。Current baselineとV001～016は不変更。既知秘密pattern scan0hit。実process main/親OS/backup gate・systemd実credential正系・IT/STとは分離し、PGPT工程完了は未宣言。

再現は421の固定JDK/Maven/m2で`sh /home/mini/codex/project1/work/pgpt_foundation_verify.sh PT-WEB-20260909-36`（既存runは上書き不可、再実行時は新ID）、終了0確認後に`python3 -B tools/quality/017_test_inbox_evidence_trace.py`、`019_test_evidence_set.py`、`018_collect_verified_evidence_set.py <run>`の順。完全な実行command・環境・source hash・各Test ID期待/実際はmanifest/同directory results.xmlへ保存。

## 探索履歴（正式合格へ算入しない）

2026-09-09、dev-foundationの未commit実装、JDK25.0.4+7/Maven3.9.12/PG18.6/JDBC42.7.13、421toolchain。選択testコマンドは`-pl src/schubert-nk-api -am -Dtest=InspectorDbCredentialTest,InspectorDatabaseCredentialLoaderTest,InspectorDatabaseConnectionsTest,InspectorCredentialLoaderTest,InspectorCredentialAccessTest,InspectorAesCredentialTest,FieldCodecTest,StorageAttributeGuardTest test`。ログは`/tmp/pgpt-inspector-database-explore-N.log`、raw出力/credential本文をGitへ転記しない。

| 探索 | 結果 |
|---|---|
| 1 | 17:30:06 JST終了1、NullAwayが必須regex captureのnullable引渡し/代入2件を拒否。BUG-131起票後、matches成功時の必須groupを明示non-null化。PT未実行 |
| 2 | 17:31:38 JST終了1、新material4/reader5＋既存AES/reader/policy28＝37件成功。DB接続のBeforeAllが空passwordの08004を28P01と誤期待しsetup1 failure、接続7 PTは未実行。BUG-132へ先行起票 |
| 3 | 17:35:27 JST終了1、API44中43成功/1 failure。SCRAM正誤/限定接続/権限/故障/並行は成功。PT208の共有fixture wire相関101と新Message100が不一致で正系も保護されdeleted0。BUG-133/YKT-104を修正前登録、Production拒否条件は変更しない |
| 4 | 17:38:43 JST終了0、API44件全成功、failure/error/skipped 0。関連Protocol5/Storage7は別集計。正式回帰ではない |
| 5 | 17:45:38 JST終了0、22.222秒、API44件全成功、failure/error/skipped 0。直接throwへ整理後の再確認。017/019証跡gate負canaryは別集計10件PASS |

探索coverageでCoderResult.throwException()の通常復帰を仮定するコンパイラ生成経路が未実行だった。isError時は同じ固定format例外を直接throwする等価な実装へ整理し、除外や偽assertionを追加しない。UTF-8不正vectorと正常vectorの両方で再確認する。

BUG-130/YKT-103はsource reviewで上限前の入力比例char allocationを先に起票し、最大65536charへ制限。入力/decoder/IO buffer消去を維持する。021専用collectorと009共有package所属・019負canaryを追加し、次正式は全31scope/10collectorで同run/source/hashを照合する。
