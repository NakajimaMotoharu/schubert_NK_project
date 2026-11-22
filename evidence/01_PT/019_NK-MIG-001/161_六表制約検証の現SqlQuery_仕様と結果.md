# 六表制約検証の現SqlQuery

NK-MIG-001、WBS-F03/2-2-b、関連P019-03、UI242/254、SS343/354。PT-MIG-CONSTRAINT001〜022。独立V002の75制約、6固定SQL、NULL・合成catalogの妥当性、列順、所有する文と行のclose、借用Connection、資源失敗の同一性・抑制順および64並行の元期待を維持。PG42838の型付き包括例外9を試験宣言の整理で是正し、PG33656の旧Mainから現SqlQueryを含む二物理への差を現Scopeで検証。

PG42840、dev-foundation、2026-11-23 JST。通常22成功、F/E/S 0、JDK25.0.4／JaCoCo0.8.15。単一execの現実CRC `ef5024c22f142612` に73/73 probe、行77、method15、class1、branch32、instruction521の全missed0。`SqlQuery` はabstractのみの自然NoCode。手動除外・exec合成なし。試験宣言を逆変換し、既存のfixtureとSQL期待値が完全一致した。SpotBugs包括型9→0、意図的ThrowableのJDBC proxy故障注入1件、PMD生8、Checkstyle0。実DB、COPY、正式451は別条件。[PG42840 manifest](evidence/PG42840-master-constraint-current-v1/manifest.json)
