# 197 NK-OPS-001 Morning親root排他境界・限定実行結果

実行日2026-09-28 JST。`dev-foundation`、source commit `587fb88a0`、PG336。Program/class/method/Test ID、RD/UI/SS、独立期待とfixtureは196を正とする。JDK25.0.4/Maven3.9.12/JaCoCo0.8.15/SpotBugs4.10.4.0、Linux host UID1000。実行command・時刻・source/test hash・終了code・入力/期待/実際・coverage・関連SSCは`evidence/provisional/PG336-morning-root/manifest.json`に記録。

| 検証 | 結果 |
|---|---|
| PG336 MROOT001～006 | 6件 F/E/S0。SS341のroot→M→全8 policy→continuation→M close→root順、M競合で後続0回、policy/continuation/null/各5箇所root異常を確認 |
| 関連既存PT | `MaintenanceFileLockTest`8、`RootStartupContextTest`9、`MaintenanceUnitStopClientTest`11、`MaintenanceUnitStopPolicyTest`7を同一sourceで実行。新6件と計41PT/5suite、F/E/S0。Batch SpotBugs BugInstance0/error0、Build成功 |
| clean JaCoCo限定値 | `MorningRootScope` branch missed0/covered2、class0/1。line missed8/covered16、method missed3/covered2。native固定root/M factoryは実Morning Unitなしで未実行。除外/期待緩和なし。全Production coverage100%不合格 |

Sanitized JUnit5 XML＋coverage1＋static1の7fileをhash再照合し、manifest SHA-256 `30e37f29d1f37e93c7991550f8e113f8d00d9925f19a17d3cd9246a747a01450`。Properties/output/credential/raw sessionは保存しない。原始実行logはGit外のpath/hashだけをmanifestへ記載。固定secret pattern scan hit0。関連新BUGなし。既存SSC-100～102の親root/全8policy境界を実装したが、実stop、UNKNOWN保全、連続A、全Unit真正配備、両backup/cleanup、permit、外部Business process、CHRは未達。これは限定PTであり正式`PT-WEB-20260925-24`/source`858713c0bf310ae8bf62078b0a1cedbce4e968db`の1964PT/53scope・全体中心48.3%を更新しない。
