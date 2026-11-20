# Expiry監査値と解放順の追補単体仕様

Program NK-BAT-001。RD DAT-009／OPS-009、UI251、SS331・332・341、SSC-304／461、WBS-F03/2-2。対象は \`ExpiryAuditRepository.Stage\`、\`Snapshot\`、\`Prior\`、\`verifySuccessfulAudit\`、\`usingJdbc\`。同じ製品物理を使用し、JDKのメモリ内で試験する。

| Test ID | 事前条件・入力・操作 | 独立期待値 |
| --- | --- | --- |
| EXPPORT-P006 | 同一フィールドの別値を二つ、単一フィールド差の値を一つ用意し、三種類の値集合へ投入 | 各集合の件数2。別 attempt は同一監査結果でも別値。結果は与えた観測値・identityの組で決まる |
| EXPPORT-P007 | WARNING、完了時刻なしのSUCCESS、観測時刻と同時のSUCCESSを照合 | 先行二件は所定のBatchRepositoryException。観測境界のSUCCESSは受理。SS341の保持済み終端条件に従う |
| EXPPORT-P008 | 取得→読み取りで独立のIOException、解放で独立のSQLExceptionを返すfixture | 読取例外の同一性維持、解放例外だけを一つ抑制、取得・読み取り・解放をこの順に各一回。SSC-304の資源所有と例外優先に従う |

PG40720で既測の26件を同一実行の根拠に含める。新3件と既26件のケースを分離し、JDK25で実行し同一JaCoCoから無フィルター計測。実DB・業務権限・保持原本・並行処理は元仕様697と該当工程で確認する。その他の未到達は現物理と分岐座標を保全する。
