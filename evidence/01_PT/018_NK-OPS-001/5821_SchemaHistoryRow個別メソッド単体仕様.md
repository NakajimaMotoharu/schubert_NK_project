# SchemaHistoryAdmission.Rowの個別メソッド単体仕様

NK-OPS-001／NK-DAT-001、WBS-G13.03／P019-01.02、RD DAT-009・SYS-002、UI212・253、SS331 §3.3／343 §9.1／354。PG43218で直接結べていなかった `installedRank`、`type`、`version`、`checksum`、`equals` を対象とする。

| ID | 操作 | 独立期待値 |
|---|---|---|
| PT-OPS-SCHEMAROW001 | 固定rank 0のSCHEMAと固定rank 5の合成SQL履歴行を生成 | SCHEMAは0／SCHEMA／version null／checksum null。SQLは5／SQL／029／-42 |
| PT-OPS-SCHEMAROW002 | 全値が等しい別行、checksumだけ-41にした別行を比較 | 同値のequalsとhashは一致。checksumが異なる行は等価にならない |

合成の値だけを使う。正規Bootstrap JARの `Row` 一クラスを実行時に読み、外側のクラスはネスト型を解決するコンパイラのみに渡す。JDBC、実DB、Flyway、原本、権限／起動、全451は別。既存PG43178のexecと合算しない。
