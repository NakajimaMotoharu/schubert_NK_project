# Batch三計測fixtureの例外型を限定した後の再試験

NK-OPS-001、SS351・354、WBS-F03/2-2-b、BUG-3588／YKT-2823。試験対象の製品クラス、入力値、固定期待値は3941の定義を使用する。再試験は `BATCHREC006～008`、`INTEGRITYMET005～007`、`RESTARTMET005～007` の9件。実際の計測fixtureから、例外を発生するカウンター登録・増分および有限並行試験を選ぶ。

対象の例外判定は合成の `Error` または `RuntimeException` をそのまま渡す。予定外の型はfixture内で失敗する。期待は旧fixture定義の戻り値、同じ例外インスタンス・増分回数、再試行なし、借用registry所有、有限worker停止。元の固定秒数、計数、labelと期待例外は変更しない。Main、計測の転送、外部監視、実プロセスは操作しない。

現候補の正規Batch JARの許可済みクラスと既存SDKだけを読み、現fixtureを固定して再試験する。三fixtureの型付き解析を実施し、未確認cast、広いchecked例外、その他の生指摘と適用性を各々記録する。製品の全メソッドやF03の全体品質をこの9件へ算入しない。実行のsource／command／終端／JUnit／静的解析と差分のSHAは結果manifestを参照。
