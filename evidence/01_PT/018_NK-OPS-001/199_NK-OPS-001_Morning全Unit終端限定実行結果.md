# 199 NK-OPS-001 Morning全Unit終端・限定実行結果

2026-09-28 JST、`dev-foundation`、source commit `67e7a8174`、PG337。Program/class/method/Test ID・RD/UI/SSと独立期待は198。Linux host UID1000、JDK25.0.4/Maven3.9.12/JaCoCo0.8.15/SpotBugs4.10.4.0。実行command、時刻、入力/期待/実際、source/test hash、関連SSC・終了codeは`evidence/provisional/PG337-morning-terminals/manifest.json`に記録。

| 検証 | 結果 |
|---|---|
| MTERMS001～005 | 新5件 F/E/S0。手書きliteralの固定8順、先頭/末尾busy、known異常redaction/unknown identity、null・wrong actor、割込0/1/8観測とflag維持を確認 |
| 関連回帰 | `MaintenanceUnitTerminationTest`9、`MaintenanceUnitStopClientTest`11、`MaintenanceUnitStopPolicyTest`7、`MorningRootScopeTest`6を同じsourceで実行。計38PT/5suite F/E/S0、Batch SpotBugs BugInstance0/error0、Build成功 |
| clean JaCoCo限定値 | `MorningUnitTerminals` branch missed1/covered9、line missed5/covered13、method missed1/covered3、class missed0/covered1。`MorningRootScope` branch0/2、line8/16、method3/2、class0/1（missed/covered）。native親成功経路と正式8 Unit未配備のため100%未達。除外なし |

Sanitized JUnit5 XML＋coverage1＋static1の7file hash不一致0、manifest SHA-256 `073268126ac698f62a456f601b3840b5836c4cfa390e8d57dbd4950dbbcf88ba`。原始logはGit外path/hashだけ、credential/raw session等は非格納、固定secret pattern scan hit0。新BUGなし、SSC-100の親全8終端読取に対応。ただし実VMは5正式Unit not-found、stop実行・M/A連続保持・broker clean journal・backup/cleanup・permit・R2/R3は未達。正式`PT-WEB-20260925-24`/source`858713c0bf310ae8bf62078b0a1cedbce4e968db`の1964PT/53scope・中心48.3%は更新しない。
