# Run / Activation 公開値原2単体仕様

Program NK-BAT-001、Main BatchRun/ MaintenanceActivation、原whole BatchRunValueBoundaryTest、OPS-009/UI251/SS331/341§3/7/343§6.13、PG-D-137/156、PT-BAT-RUNVALUE001/002。費用WBS-F03追加資格、artifact ownerは485、元P017費用へ再配賦しない。

1. cutoffBoundsNullsAndFixedRunDiagnostic: UUID(0,16)固定synthetic。0001-01-01、1582-10-10、9999-12-31T23:59:59.999999Zは許容、年0・10000・nano1はIllegalArgumentException。id/cutoff accessorは入力値そのもの、診断は固定BatchRun[identity/cutoff=<redacted>]。二nullはinvariant拒否NPEをassertThrows（catch正常化禁止）。期待境界は設計のPostgreSQL timestamp年/µs契約から手書き、production methodでexpected生成しない。
2. activationNullsValueAccessorsAndFixedDiagnostic: UTC2026-09-12 15:00はJST翌13日00:00、LocalDate.of(2026,9,13)が独立期待値。run/id accessorは固定入力、診断MaintenanceActivation[identity/cutoff=<redacted>]、二null拒否。値自体は実行権限・所有・freshnessを証明しない。

Main2/Test1全49行/JDK値/JSpecifyとJUnitのみ、worker/DB/network/Root/鍵/actual4/反射なし。原2全体実行、method抽出/新fixture/skip/旧exec合算/独自coverage除外0。PG28166のRun未網羅B3/L2/M1とActivation未資格を閉じる必要品質で、旧成功確認目的の再演ではない。

Commandは共通工具prestyle/prepare/static/preflight/run、独立post。Root release25 NullAway/ErrorProne/Werrorと全静的規約、独立sourceanchor適用判定、source固定後にone whole run。全physical2/CRC/class-init/XML/FESabort/line-method-class-branchと例外・nullの期待値を検証し、未網羅は失敗や未知と区別して保持。OS/JDK/tool/branch/commit/終了code/command/input/output/hashは各stage manifestと独立manifest。工程全体451/CHR/native/正式1964-53は本2件だけで更新しない。
