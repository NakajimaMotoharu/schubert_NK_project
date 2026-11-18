# InspectionProgress／InspectionExecution公開値の単体テスト仕様書

NK-DAT-001、P004-04、QA-046、SSC-049、SS324/331/341/351、UI251、451、YKT-2673。歴史PG18070の関連ケースと元期待を保持し、現行Javaの値型境界に独立五件を配置する。

| Test ID | 対象 | 独立期待値 |
|---|---|---|
| PT-OPS-INS-VALUE-005 | InspectionProgress constructor/accessors/toString | 時刻とUUIDの代用値、0とLong.MAX_VALUEからの非負計数、固定減算、負計数・逆転・合計差・cursor有無の逆・nullを拒否、固定文字列 |
| PT-OPS-INS-VALUE-006 | InspectionProgress equals/hashCode | 内容同じ別instanceで既保存値を取得し、run・cursor・計数・完了の違いに一致しない |
| PT-OPS-INS-VALUE-007 | InspectionExecution constructor/exitCode/status/lastConfirmed/toString | 固定5分類、0/10/50、確認済み観測の保持、未確認は空、固定診断 |
| PT-OPS-INS-VALUE-008 | InspectionExecution constructor | 正常／警告と記録済み完了・保護件数の矛盾、nullを拒否 |
| PT-OPS-INS-VALUE-009 | InspectionExecution equals/hashCode、Status | 同値検索と二成分差、5名称・順序・未知／null拒否を固定値で確認 |

DB、SQL、実Inspector、並行Actor、外部再送、nativeは外側の別試験。値のcompleteは永続ENDの型表現に限る。独立した期待値は固定件数、診断と序数表。現Mainは変更しない。使用classをすべて記録し、依存InspectionRunは対象二型のcoverageへ足さない。

現行JDK25で通常5件、独立XML/CRCと未フィルタ計測。生成Codeに不足があれば個別method/branchと未達を保持してから是正可否を判断する。元exec、当新runと別sourceの合算はない。実行日時、環境、command、commit、hashは結果書とmanifestを参照。
