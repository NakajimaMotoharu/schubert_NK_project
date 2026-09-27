# PG305 backup専用資格情報 PT仕様

Program NK-OPS-001、shared Bootstrap `InspectorCredentialLoader.readBackupPgpass`と共用保持inode reader。RD BAK/BKO/OPS009、UI251、SS341 §6.1/343 §6.6、SSC090、PG-D-305。試験class BackupCredentialLoaderTest。Production expected生成なし、literal ASCII公開pgpass vector/明示metadataを独立oracleとする。合成UID/ACLと実VM配布を区別する。

| Test ID | method/目的・fixture・入力/操作 | 独立期待値 |
|---|---|---|
| PT-OPS-BACKCRED001 | literalAndOwnedCopy、固定backup-pgpassの公開literalを読む・返却をzero | 元file不変、完全byte一致、open/close各1、作業buffer全zero |
| 002 | boundedSource、1/65536byte・chunk17、0/65537byte | 正の両端を全byte照合、範囲外固定拒否 |
| 003 | fixedNameMissingAndNoFallback、専用file欠落・別DB file存在 | 別材料fallbackなし、content open0 |
| 004 | everyIoFailureClears、属性/open/read/zero/短長/close/final故障 | 固定非成功、buffer消去、取得したchannel全close |
| 005 | namespaceAndSecurityFailures、ACL/readonly/device/root入替え | 権限・同device・前後root不一致を拒否 |
| 006 | symlinkAndHardLinkRefused | final symlink/nlink2を読む前に拒否 |
| 007 | closeFailureAndNullContracts、entry close障害/constructor null | close失敗を成功にしない、nullは契約違反 |
| 008 | independentConcurrentCopies、32呼出/8thread | 全copy独立・完全byte一致・消去後も元不変 |

実行環境はJava25.0.4/Maven3.9.12/Linux、JaCoCo0.8.15、SpotBugs4.10.4.0、NullAway/lint/format共通gate。25限定PT command/branch/source/hashと失敗履歴はprovisional/PG305/manifest.json。新methodのline/method/instruction missed0、branch定義0。class全体と全Productionのcoverage合格は本限定実行だけでは認定しない。関連障害なし（未完備collector初回canary1errorは合格不算入）。

PT-OPS-NATIVE-022は隔離VM marker/固定専用User/LoadCredential/ProtectSystem=strict/RuntimeDirectory0700を使う。独立libpq 0440拒否→0600公開ではない専用材料→Production工具dump/list成功、全子終了後copy消去/unlink/dirsync、Unit inactive/exit0を確認。secret/DB dumpをGitへ格納しない。nativeprobeはtest-onlyのcopy組立であり、Production worker/親全backup controller・manifest/DB両step/7世代/総30分/全gate/実NK CHRは未達。
