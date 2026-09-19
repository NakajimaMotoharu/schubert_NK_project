# NK-OPS-001 private子directory新規作成PT

PG186/SSC068、RD BAK/BKO/OPS009、UI251、SS333§7.6/341§6.1/343§5.3。対象DirectoryCalls.createPrivateDirectory、LinuxDirectoryCalls.createPrivateDirectory、OwnedTransferDirectory.createPrivateChild。Production変更前・未実装/未実行。

独立fixtureは実Linux temp親、公開合成byte、操作前後unix dev/ino/mode/uid、記録call inventory。Productionでexpectedを生成しない。通常umaskで0700（owner権限縮小は別失敗）、空directory、同deviceと保持child FDを確認。既存0750/openDate/private0600 fileのoracleは不変更。

| Test ID | method | 観点・入力/操作/独立期待 |
|---|---|---|
| PT-OPS-CDIR-001 | nativePrivateCreation | mkdir0700→openDirectory→child sync→parent sync、返却child継続所有/親borrowed、mode・実owner・空集合、childから作成した公開fileで能力確認 |
| PT-OPS-CDIR-002 | existingEntriesPreserved | directory/file/symlinkの同名拒否、inode/mode/byte/target不変、既存open/repair/deleteなし |
| PT-OPS-CDIR-003 | nameNullAndClosed | null/空/dot/dotdot/slash/NUL/closedはnative mutationなし、native null/不正name/不正FD/長名を拒否 |
| PT-OPS-CDIR-004 | everyNativeFailure | mkdir/open/child sync/parent syncの各位置IO/unknownRuntime/NPE/Error、取得済FD close1・未取得0、partial保全、親継続 |
| PT-OPS-CDIR-005 | compoundFailures | sync bodyとowned child closeのknown/unknown/same throwable、元identity/固定secondary/close優先順位、close再試行なし |
| PT-OPS-CDIR-006 | retainedParentCapability | 親path差替え後も元保持parentのみに生成、replacement/外部不変、開いたchildは独立close |
| PT-OPS-CDIR-007 | unsupportedAdapter | default未対応private能力はUNAVAILABLE、0750既存能力へfallbackせずmutation0 |
| PT-OPS-CDIR-008 | concurrentNewOnly | 同じnameへ複数同時要求、成功1/残collision、単一inode・全FD解放、private同期を外部synchronized対象で妨げない |

環境JDK25.0.4/Maven3.9.12/Ubuntu26.04.1/Linux7.0.0-31/glibc2.43、dev-foundation。Storage選択test→全reactor、line/method/class/branch100%・NullAway/Enforcer/Spotless/SpotBugs、全fail/error/skip0・trace/collector負canaryを確認する。command/対象source/日時/exit/入力期待実際/coverage/BUG/証跡path/hashは032と018/evidence/manifest.jsonへ記録する。native入場の通常利用者PTは専用backup実owner/root配布・archive作成の成功ではない。新8PT/OPS1部分成果は正式認定後だけ加算する。
