# 214 NK-OPS-001 Morning明示同run再開・限定実行結果

2026-09-28 JST、branch `dev-foundation`、source/test commit `0c47d6124`。対象と独立期待は213。Linux host UID1000、JDK25.0.4、Maven3.9.12、Node24.19.0、JaCoCo0.8.15、SpotBugs4.10.4.0。

選択`MorningResumeAdmissionTest`9＋`MorningControlScopeTest`11＋`MorningDatabaseSessionTest`14＝34PT、failure/error/skipped0、Batch SpotBugs0、Maven exit0。MRESUME001/009は専用DB owner取得前のdurable file操作0、DB→File→参照→後続と逆順close、MRESUME007は並行後続中の両owner保持を手書きevent/latchで確認。MDB014は実PostgreSQL V018の同run batch履歴を用い、元cutoffと同JST業務日の+1秒は整合、翌JST業務日は不整合と確認した。SS331 §3.12はbatch履歴をbusiness_dateで投影するので、秒単位の原本cutoff一致をDB照会へ誤要求しない。file graphの原本契約は別試験で扱う。初回32PTはBUG-317の排他順序違反を見落としていたため合格へ算入しない。試験開発中の中間失敗・compile失敗も最終34件へ算入しない。

456へsecurity/DB資源境界の全回帰triggerを事前記録し、同一sourceでProduction6の `clean test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check` を実施。Protocol80/17suite、Storage149/21、Bootstrap175/22、API742/123、Web555/85、Batch693/83、合計**2,394PT/351suite**、failure/error/skipped0、全6 SpotBugs BugInstance0、Maven exit0。原始logはGit外`/tmp/pgpt-pg345-six-final.log`、SHA-256 `bb1bd64737786bc7dd618a5353aeb8dee8f384635534252fec15459de7dde8f3`。同run/sourceのsanitized JUnit351＋coverage2＋static6＝359 fileを`evidence/provisional/PG345-morning-resume/`へ保存、manifest SHA-256 `0a216c448b0f922c0fa3933263c5d74b3ea249cdec9e65edffa163bd4136fe78`。全manifest path/hash再照合、秘密pattern6種0、JUnitのproperties/stdout/stderr/失敗payloadは保存しない。

4指標coverage missed（branch/line/method/class）はProtocol `0/0/0/0`、Storage `0/0/0/0`、Bootstrap `37/11/4/0`、API `1/19/3/0`、Web `1/19/3/0`、Batch `13/197/80/10`。変更本体`MorningResumeAdmission`は`1/5/1/0`、`MorningControlScope`は`0/17/6/0`、`MorningDatabaseSession`は`0/4/3/0`、`MorningNewRunAdmission`は`3/13/2/0`。native正経路・外部実Unit等の未被覆を除外せず、全体4指標100% gateは不合格。

BUG-317はDB前の原本mutationを修正前起票→sourceで排他順を是正→選択と全6で再試験済み。ただしYKT-250の`MaintenanceRunFiles` complete/retire・GCのProduction callerは未接続で、接続時の同順序oracleと外部実測を残すため横展開台帳は対応中とする。関連SSC-055/094/105の全親工程も完了扱いにしない。

外部`MorningProcessMain`はread-only fail-closed exit30のまま。実VMの保留run、旧current、PG323 test-only Morning Unitは不変更。固定8のWeb/API/Cleanup/Inspector/Expiry5件は未配置、Artemis inactive。実M/A/8停止/current INVALID、backup/Cleanup/permit、Web/API外部起動、実NK CHR-A01/L01は未達。正式認定source `858713c0bf310ae8bf62078b0a1cedbce4e968db`、run `PT-WEB-20260925-24`、1964PT/53scope、加重中心48.3%は据置。PG/PT・IT/ST完了を宣言しない。
