# NK-OPS-001 root起動A同一scope PT仕様（PG372）

対象予定class `RootServiceAdmissionScope.execute`と`RootServiceLauncher.preflight`の`StartupAdmissionFile.tryExclusive`結線。RD SYS-002/004/OPS-009、UI212/251/253、SS341/342§4.2/343§6.15、SSC086～089、471 R1/D04/D05。root actor capture後に既存固定Aを借用し、その同一callback内でroot再確認→固定NSS/release/current permit/argv→root再確認を行う。callback通常return後にもrootを再確認する。reserved A descriptorは借用で、まだproof/同PID execへ渡さない。A競合・未知失敗・正常callbackの全てで現行入口exit30を維持。

| Test ID | fixture/input | 独立期待値 |
|---|---|---|
| PT-OPS-RASCOPE001 | 合成root gate＋排他Aの1 callback | root→A内root→work→A内root→A返却→rootの順、同じ予約FDを一度だけ借用 |
| PT-OPS-RASCOPE002 | A競合でOptional.empty | work0、固定IOException・非成功 |
| PT-OPS-RASCOPE003 | A callbackが予約外FD127/0/65536 | work0、固定IOException。FD128と65535は受入境界 |
| PT-OPS-RASCOPE004 | work中IOException/既知root再確認失敗 | 成功へ変換しない、A所有portへ例外が戻る |
| PT-OPS-RASCOPE005 | callback後の外側root再確認失敗/偽success | exit成功にしない。A正常解放済でも後段ゲートを省略しない |
| PT-OPS-RASCOPE006 | null依存・反復 | null契約拒否、静的共有A所有なし。既存`StartupAdmissionFileTest`のnative/close観点を併用 |

期待順/FD境界はSS343のA予約128～65535と同PID置換前後のroot再確認から、独立イベント列/literalで固定する。Production callbackをexpected算出に使わない。JDK25.0.4/Maven3.9.12のBatch選択PT・既存StartupAdmissionFile関連PT・SpotBugs/JaCoCoを実行し、security6module固定source回帰を後続255へ保存。真正root Unit・実A/permit/current/exec・coverage全体100%は別gate。秘密fixtureなし。
