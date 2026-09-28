# 212 NK-OPS-001 Morning current INVALID・限定実行結果

2026-09-28 JST、branch `dev-foundation`、source/test commit `3f300a84c`。対象・独立期待は211。Linux host UID1000、JDK25.0.4、Maven3.9.12、Node24.19.0、JaCoCo0.8.15、SpotBugs4.10.4.0。

選択`MorningCurrentInvalidationTest`6＋`MorningControlScopeTest`11＝17PT、failure/error/skipped0、Batch SpotBugs0・Maven exit0。固定UUID/手書きevent oracleにより、親M→原本→固定8停止→A→fresh8→INVALID/readback→後続workの順、writer失敗時work0、全owner close、wrong binding/既完了/null/重複epoch拒否を確認。`StartupPermitFiles`自身のatomic/force/ACL/byte試験は既存試験で別扱いであり、この17件は実OSのM/A/8Unitや実tmpfs書込みではない。

security/現在許可原本の横断変更triggerを456へ事前記録して、Production6を同一sourceで `clean test org.jacoco:jacoco-maven-plugin:0.8.15:report com.github.spotbugs:spotbugs-maven-plugin:4.10.4.0:check`。Protocol80/17suite、Storage149/21、Bootstrap175/22、API742/123、Web555/85、Batch682/82、合計**2,383PT/350suite**、failure/error/skipped0、全6module SpotBugs BugInstance0、Maven exit0。Batch前に実施した未指定prefixによるMaven preflight不合格は試験未実行、続く2,383件の全runは最後のtest/comment変更前のため最終認定へ不使用。最終run `/tmp/pgpt-pg344-six-final.log` SHA-256 `27aa800ace591a765120641376358cf89dc47c8ed8b656d58c88945bb8efda69` に限定する。

4指標coverage missed（branch/line/method/class）はProtocol `0/0/0/0`、Storage `0/0/0/0`、Bootstrap `37/11/4/0`、API `1/19/3/0`、Web `1/19/3/0`、Batch `11/174/69/7`。変更本体`MorningCurrentInvalidation`は`2/9/2/0`、`MorningControlScope`は`0/12/5/0`。未被覆はnative正経路・実root/Unit等を含むため、coverage100% gate不合格であり除外設定はない。

sanitized JUnit350＋coverage2＋static6＝358fileを `evidence/provisional/PG344-morning-invalid/` に保存。manifest SHA-256 `78970b43fa59e7360058346253eacd26e165b0c3d0812acf49cfdeebeac0d3b5`。JUnit properties/stdout/stderr/失敗payloadを保存せず、実行時のraw秘密・cookie/token/session/InvocationIDはGit外。manifestの全file path/hashを再照合済み。関連BUG-315/YKT-248（既存未完了）、SSC-089/105。新しい実装済み承認仕様違反はこのrunで未発見。

外部`MorningProcessMain`は依然read-only fail-closed exit30で本scopeを起動しない。VMの保留run・旧current・既存PG323 test-only Unitは不変更。resume選択、固定8の未配置5Unit、handleなしUNKNOWN/hard-timeout、Artemis clean journal、実backup/Cleanup、permit、Web/API外部起動、実NK CHR-A01/L01は未達。正式認定source `858713c0bf310ae8bf62078b0a1cedbce4e968db`、run `PT-WEB-20260925-24`、1964PT/53scope、加重中心48.3%を据え置く。PG/PT/IT/ST完了を宣言しない。
