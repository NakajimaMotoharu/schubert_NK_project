# Outbox純値二型の静的品質確認仕様

NK-OPS-001／NK-MSG-002。WBS-F03/2-2、F03/criterion/quality、SS311・324・332・354、451、SYS-004。対象はAPIの `OutboxRetrySchedule` 全method、`OutboxDispatchReport` のconstructorとrecord生成method、および同packageの `@NullMarked` 宣言。

| Test ID | 入力と操作 | 独立の期待値 |
| --- | --- | --- |
| PT-F03-OUTBOX-STAT-001 | 現Coreから二Mainとpackage-infoを固定し、JDK25のjavac、Checkstyle、formatter、PMDを既定規則で実行 | javacと各静的工具が終了0。Checkstyleの三入力が一致し指摘0、PMDの処理3・指摘0・エラー0。生成物は二型とpackage-infoの3物理。期待物理名は入力Javaの型宣言とJDKのpackage-info表現から固定 |
| PT-F03-OUTBOX-STAT-002 | 同3物理にSpotBugs4.10.4 Max/Low。補助依存にコンパイル投入済みのjspecify | 終了0、ClassStatsの全集合が物理名と一致、BugInstance、Error、MissingClassが各0。451記載のXML後条件による |
| PT-F03-OUTBOX-STAT-003 | 先行XML・補修後XMLの保全と独立比較 | 旧XMLはNullMarked欠落1件。補修後は同物理SHAで欠落0。再実行は対象SpotBugsと、その同一物理を生成するjavacのみ |

動的な正常・境界・例外・null・並行・再送の判定およびcoverageは当仕様の実施対象外。再送とカウンターの既存証票はWBS66実行記録221–222が保持する。現scopeのNullAway・同source/同runのPTとcoverage・全API/WebのClassStats・正式451は各残条件に従う。

コマンド・JDK・source・SHAはPG40688とPG40690のmanifest、独立判定はPG40692のmanifestを参照する。
