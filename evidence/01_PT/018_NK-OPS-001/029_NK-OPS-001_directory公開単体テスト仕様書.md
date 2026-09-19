# NK-OPS-001 既存子directory公開PT

2026-09-19、SSC065/PG-D-176、未実装・全not-run。RD BAK/BKO/OPS009、UI251、SS311/333§7.5/341§6.9。対象Storage.OwnedTransferDirectory.publishChildと所有scope lambda、既存LinuxDirectoryCallsのdirectory rename利用。前の正式結果へ加算しない。

fixtureは実Linux temporary親/子と保持FD、独立literal `pending`/`ready`、公開合成byte `{65,10}`、記録済inode/dev/modeと期待順序openDirectory→publish→sync→close。production methodでexpectedを作らずFiles.readAttributes/独立byteで操作前後を照合する。root/backupUIDやarchive真正性をこの低位PTで証明しない。

| Test ID | method | 目的・入力/操作・期待 |
|---|---|---|
| PT-OPS-PDIR-001 | nativeDirectoryPublication | 既存pendingとfileを保持、公開後readyの同inode/dev/byte、pendingなし、親借用継続 |
| PT-OPS-PDIR-002 | noReplaceAndSourceType | target directory/file/symlink衝突は双方不変。sourceなし/MISSING、file/symlink非成功・外部不変 |
| PT-OPS-PDIR-003 | nameNullAndClosed | 各引数の空/dot/dotdot/slash/NUL/null、同名、closed親をnative操作なしで拒否 |
| PT-OPS-PDIR-004 | everyNativeFailure | 4操作各位置の既知StorageIO、unknownRuntime/Error、所有child一度close・親保全 |
| PT-OPS-PDIR-005 | uncertainPublication | rename成功後syncまたはclose失敗ではready現物保全・非成功、逆操作なし |
| PT-OPS-PDIR-006 | compoundFailures | body/close同unknownの元identity、known body＋unknown close優先、固定secondary・秘密診断なし |
| PT-OPS-PDIR-007 | retainedParentCapability | 親元path差替え後も保持親側だけの操作、replacement側不変 |
| PT-OPS-PDIR-008 | concurrentNoReplace | 異なる8pending→同ready、成功1/衝突7、全original byte/inode保存、親/子FD漏れ0 |

実行はJDK25.0.4/Maven3.9.12・dev-foundationでStorage選択test→全reactor。全branch/method/line/class100%、既存file oracle回帰、static0、失敗/skip/not-runは不合格。対象commit/日時/command/終了code/coverage/BUG/証跡hashは030結果と018/evidence/manifest.jsonへ実行後記録する。単体実装・証跡の完了前にSSCを完了にしない。親backup制御・全bundle確定・IT/STは別残件。
