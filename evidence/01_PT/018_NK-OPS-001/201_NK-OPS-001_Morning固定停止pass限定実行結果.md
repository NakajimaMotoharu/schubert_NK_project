# 201 NK-OPS-001 Morning固定停止pass・限定実行結果

2026-09-28 JST、`dev-foundation`、source commit `d068d94e4`、PG338。Program/class/method/Test ID、RD/UI/SS、独立期待/fixtureは200。Linux host UID1000、JDK25.0.4/Maven3.9.12/JaCoCo0.8.15/SpotBugs4.10.4.0。実行command/時刻、source/test hash、入力/期待/実際、終了code・関連SSCは`evidence/provisional/PG338-morning-stop-pass/manifest.json`に記載。

| 検証 | 結果 |
|---|---|
| MPASS001～009 | 新9件 F/E/S0。固定8のclient→whole-Unit→全8fresh順、policy失敗0stop、client非0/Unit未終端、UNKNOWN再回収と別thread保持、割込flag、null/wrong actor、UNKNOWN→非0を確認 |
| 関連回帰 | `MorningUnitTerminalsTest`5、`MaintenanceUnitStopClientTest`11、`MaintenanceUnitTerminationTest`9、`MorningRootScopeTest`6を同一sourceで実行。計40PT/5suite F/E/S0、Batch SpotBugs BugInstance0/error0、Build成功 |
| clean JaCoCo限定値 | `MorningStopPass` branch missed1/covered11、line missed6/covered32、method missed1/covered6、class missed0/covered1。実root/native固定Unitの成功経路は未実行。除外なし、全Production coverage100%未達 |

Sanitized JUnit5 XML＋coverage1＋static1の7file hash不一致0、manifest SHA-256 `d17031d4df925e45e0b1df1fe3f45fa1ee93c2419c309fc1acf06eac3d6fb140`。Git外の原始logはpath/hashのみ、秘密/credential/raw sessionは保存せず、固定secret pattern scan hit0。新BUGなし、SSC-100～102に対応。`UNKNOWN`の既得AttemptはM-owning callbackから正常帰還しないが、実親M/A/current失効との連続結線、startがhandleを返す前の不明、正式8 Unit配備・実stop/終端、journal、backup/cleanup/permitは未受入。R2/R3・正式`PT-WEB-20260925-24`/source`858713c0bf310ae8bf62078b0a1cedbce4e968db`の1964PT/53scope・全体中心48.3%を更新しない。
