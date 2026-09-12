# NK-OPS-001 private保持file・名前付き非上書き公開の単体テスト仕様書

PG-D-153/SSC-049（先行67148c13）、OPS-009/UI251/SS311・333 §7.3/343 §6.10。DirectoryCalls.createPrivateFile、LinuxDirectoryCalls同method、OwnedTransferDirectory.createPrivatePart/publishAs/unlinkEntry。実Linux/libc/孤立directoryと公開SPI faultのみ、任意本番fileは対象にしない。size/hash/root/ACL/同run等は上位publisherが行う。

| Test ID | method | 入力・操作・独立期待値 |
|---|---|---|
| PT-OPS-PFILE-001 | nativePrivateCreation | create0600/regular/nlink1・保持FD書込/読取とCREATE_NEW衝突、既存通常0640不変。期待Unix bit値/固定byte literal |
| PT-OPS-PFILE-002 | atomicNoReplace | 固定名へのpublish→元part不存在/target内容一致、既存target/symlink衝突→両者不変、target外のfile不変。Java rename代替なし |
| PT-OPS-PFILE-003 | scopedOwnership | callback正常/IO/Runtimeとentry close、全owned FD解放・borrowedroot生存。保持inodeと名前交換先を混同しない |
| PT-OPS-PFILE-004 | nameAndNullContracts | empty/dot/dotdot/slash/NUL/null/UUID null/operation null/closedを無操作拒否。任意階層/root削除なし |
| PT-OPS-PFILE-005 | faultAndUncertainOutcomes | create/open/close/publish/unlink/syncの各位置、rename後sync失敗でtarget保全、unlink後sync失敗で不存在を非成功扱い。故障を成功へ補完/逆操作しない |
| PT-OPS-PFILE-006 | retainedNamespace | root名を別dir/symlinkに交換しても保持元directoryにだけ作用。親の現在namespace照合を本部品の機能と偽らない |
| PT-OPS-PFILE-007 | concurrentSinglePublication | 32個の独立private part→同targetへ競合、成功1件・loser31part保全、結果byteは独立winner入力と一致。有限wait |
| PT-OPS-PFILE-008 | unsupportedAndNativeArguments | 未対応default private createは資源/operation0回のUNAVAILABLE、nativeのsingle-segment/errno/closeを検証。既存public create0640の契約は不変 |

line/method/class/branch100%、NullAway/SpotBugs/format、failure/skip0、無除外。Storage+Batch探索と全reactor正式run、019の独立OPS/Storage所属・全method inventory/非PASS拒否、018全scope/hashを016/manifestへ記録。Expectedはliteral byte/Unix bit/native後条件と独立resource数から作り、production生成値を使用しない。root配布・OS lock/子unit/backup/publisher運用完了は別の未完了gate。
