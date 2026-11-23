# 停止観測値のJava列挙カタログ独立PT仕様書

NK-OPS-001、F03、SYS002/004、OPS009、UI251、SS341 §5、SS343、SSC100、451。対象は `MaintenanceUnit.values/valueOf/serviceName` と `StopGateFailure.values/valueOf`、`StopGateException.reason/getMessage`。PG43408で既定JaCoCoから除かれた生成3メソッドを確認したため、通常の列挙型の入力契約を明示して補う。表示や制御の外部契約を追加する設計変更はない。

| Test ID | 事前条件と入力 | 独立期待値 |
| --- | --- | --- |
| PT-OPS-MCATALOG001 | 固定停止順の8つのJava名とサービス完全名を手書きした表。名前の完全一致で値を引き、異なる形式として実際のサービス名とnullを指定する。 | Java名は CADDY、WEB、API、CLEANUP、INSPECTOR、EXPIRY、BACKUP、ARTEMIS の順。各名前の結果は既存の独立仕様166と同じ8つの完全サービス名を返す。サービス完全名でのenum検索はIAE、nullはNPE。 |
| PT-OPS-MCATALOG002 | 固定5理由名。値の配列の先頭を別理由で上書きしてから取得し直す。小文字と末尾空白付き、nullを個別に指定する。 | MALFORMED_STATE、NOT_STOPPED、COMMAND_FAILURE、TIMEOUT、INTERRUPTED の順と全値の検索一致。元のenum順は変更されない。例外は選択理由を保持し、固定診断文字列は `application stop check failed`。別表記はIAE、nullはNPE。 |

両試験ともJVM内の合成値を使う。例外と欠落は独立期待に記載。並行動作の証拠は継続実行する既存MSTOP007。再送、DB、停止、設置、実機と外部の監視はこの値契約に適用しない。元MSTOP001～007の期待値とMSTOP008実経路の保留を維持。

Java 25.0.4、JUnit Platform 1.13.4、JaCoCo 0.8.15。既存の正規Batchを照合し、当該四物理と手書きfixtureだけの暫定実行を行う。全9件、同一source・単一exec・CRC、生四指標、F/E/Sなし、format/lintの結果と実行command／日時／hashはPG43410の結果に記録する。正式451・同環境判定は別条件。
