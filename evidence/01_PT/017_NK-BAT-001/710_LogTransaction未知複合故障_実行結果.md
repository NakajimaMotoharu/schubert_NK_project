# NK-BAT-001 Log transaction複合故障 実行結果

2026-11-06T09:55:54.315806+09:00。SSC337 / BUG2317・2318 / YKT2062・2063。限定PG/PT完了、実DB/native・全F03・451・NK-BAT全体は未受入。

Production Main `d8ff9efb16a7da1b073bdf9770487e3e6415b636`、Test/工具 `1707d175a3a1934d168974fe5a82a962e042f285`。Main/Test SHAはPG20138 manifest inputHashesへ固定。実行はprofile713のprepare/static/run/post（共有012 qualifier、JDK25.0.4、Maven3.9.12、JUnit1.13.4、JaCoCo0.8.15）。OS・環境・command・終了code・XML・exec・class CRC・hashはPG20138公開manifestと関連safe成果物で追跡する。Test IDと全19methodは仕様709の一意表を使用。

|指標|最新同一source/run実測|
|---|---:|
|JUnit実行/成功|19 / 19|
|Failed/Error/Skipped/Aborted|0 / 0 / 0 / 0|
|Line|156 / 156|
|Method|15 / 15|
|Class|3 / 3|
|Branch|68 / 68|
|物理class|5（abstract interface2もreportへ保持、実行code無し）|
|独立post|0|

JDK memory JDBCの公開executeでSS331固定SQL/行literal、SS341の既知/未知priority表、同一Throwable・suppression無効・rollback→復元・commit後非rollback・borrowed close0・null/期限/割込・独立connection並行を検証。期待値をProductionから生成しない。225資源vector等のループをTest件数に加算しない。storage依存・native flag・旧exec合成なし、held4 probe0。全分岐網羅はこの5物理classの現source範囲であり、実DB/他classの免除ではない。

PG20112 Main-only compile/NullAway0とPG20114六module SpotBugs0/1844 class exactを現Mainで保持。PG20137は生PMD43/Checkstyle0/processing0。43件すべてをsource/行/目的/設計で個別判断し、適用違反0、ルール抑制追加0。未分類を0に補填していない。latest Testとstatic inputHashesは一致。

YKT2062はBatch Main全14候補・実rollback9。Log1修正、既typed policy3・正常readonly rollback5・commentのみ5は個別source根拠で非該当。YKT2063は新Test全19method/helper/recordの15命名/literal違反を1707d175で是正し、値固定の逆変換証明と最新whole19再試験を保存。

修正前PG20104は真正exit1・19件/5failed、公開manifest 0bc64058941c5b0b63e1023264f8d609d7f8357c328abe094e65a815e7a6998d。これをPASSへ変更しない。PG20118は本体greenでもpostが不要storage依存で1のため未受入。依存を除きPG20128 post0、その後Test style是正後の最終資格はPG20138のみ。各19を加算せず、旧execを合成しない。GJF改行差・publisher初回拒否等の工具再試行も元証跡のまま別記。

根拠: `evidence/PG20138-log-tx-style-v1/manifest.json` SHA256 30a351acd496e229ee58a42e99fa31cfbd23c590b989dcfdfd6b4aa721a309b8、本結果の独立metadata crossjoin `evidence/PG20142-log-tx-finite-closure-v1/manifest.json` SHA256 3cb7748fca73995c237bc0c6ef67af39383c8b1916f42251621d5de26d17a01d。原正常compile/SB・static・再現・oracle変換は各元manifestのsource/hashへjoinし、成功確認の再実行なし。

正式1964PT/53scope、歴史17/190、新leaf0、工数率null。新しい是正Main1の全source限定資格を技術成果として別計上し、旧46成分が現D8で全部再受入されたとはしない。QA051 final・Root/VM/原本DB/Backup/鍵・cohort・held dynamic4等のHOLDは継続。
