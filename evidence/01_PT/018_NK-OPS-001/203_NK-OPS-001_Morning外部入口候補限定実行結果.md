# 203 NK-OPS-001 Morning外部入口候補・限定実行結果

2026-09-28 JST、`dev-foundation`、Production source commit `3daf286ee`、PG339。対象・独立期待値・Test IDは202。これはProduction Morning全工程の受入ではない。

| 検証 | 実測 |
|---|---|
| 選択PT | `MorningProcessMainTest`5、`MorningServiceUnitTest`3、`MorningRootScopeTest`6、`MaintenanceUnitStopPolicyTest`7、計21件/4suite F/E/S0。Batch SpotBugs BugInstance0/Error0、Build成功。`/tmp/pg339-mmain-clean-fixed.log`をGit外に保持しSHAのみmanifestへ記録 |
| JaCoCo限定 | `MorningProcessMain` branch missed0/covered2、line missed2/covered7、method missed3/covered1、class missed0/covered1。native public main/constructor等未被覆で4指標100%未達。除外なし |
| host別process | JDK25.0.4・UID1000で実`MorningProcessMain`を空argv起動。`--enable-native-access=ALL-UNNAMED`付き最終runはexit30、stdout/stderrとも0 byte。途中のPATH未設定`java`不実行、およびclass pathに自身のclasses欠落の失敗試行は合格へ算入しない |
| 実VM候補構文 | 候補Unitを隔離VM `/tmp/pgpt-morning-339.service`に配置し`systemd-analyze verify` exit0。host/VM同一SHA-256 `5debc9401e3f3db636709f76d5496228130792e1de1f902248d88992cabd31ec`。未install/未enable/未起動。生成runtime archiveもhost/VM同一SHA `739fd661af6245da8847731685f037d73b244d619beabd812a4167396b02c3fe`、VM `/tmp`展開のみ |
| 正規既存Unit（BUG-314/YKT-247） | `schubert-nk-morning-controller.service`はloaded/inactive/MainPID0、`/etc/systemd/system`のPG323 test-only `NativeMaintenancePreflightProbe`をExecStartとするoneshot。短縮名誤照会の「Morning not-found」を撤回。既存Unitは上書き・drop-in変更・起動せず、PG339候補のProduction受入と混同しない。固定8のWeb/API/Cleanup/Inspector/Expiryは正規名でnot-foundを再確認 |

Sanitized JUnit4 XML、coverage1、static1の6file全SHA再照合済み。manifest SHA-256 `2ee9e7e8fbf69d64ee8cb60346277f733b5d3ddc61639cd930a754f5dfb3305b`。実行日時・OS/tool・branch/source commit・command・終了code・input/期待/実際・coverage・BUG/SSC・file hashは`evidence/provisional/PG339-morning-candidate/manifest.json`。原始log、raw Unit/journal、credential、session/token、秘密値をGitへ格納しない。

R2/R3、全8実停止、M/A/current失効、clean journal、同run backup/Cleanup、permit、外部API/Web、実NK CHR-A01/L01は未実施。正式認定 `858713c0bf310ae8bf62078b0a1cedbce4e968db`/`PT-WEB-20260925-24`/1964PT/53scope/中心48.3%は据置。
