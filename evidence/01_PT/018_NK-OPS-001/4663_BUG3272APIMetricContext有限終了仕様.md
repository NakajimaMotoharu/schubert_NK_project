# BUG-3272 API MetricContextの有限終了とmode

WBS-F03/2-2、P018-09、UI252、SS351/354、元1815・2845、APIMCTX001〜033。Core bcc9e0673287c51950ecab9b36350abfcd4b2c69。021/023/024/033の外ExecutorService TWRを外し、元release・shutdownNow・await30秒を唯一のworker終了とする。033は未終端workerのままcontextを再closeせず、成功時は既registry closeを検証。同thread、競合、stop未確認、初期化失敗・回収の元全判定を維持。

APIMCTX004は独立PG39230とSS351によりDEBTf/STANDAQcを許可mode同hash異値として入力し、CONFIG_INVALIDと取得前拒否を確認する。元null・unknownを保持。既の純粋SDK登録、数値、phase、レジストリ所有、標準のgolden textは外部から独立。Main改変なし。JDK25.0.4／Maven3.9.12／Micrometer1.17.1／Prometheus1.7.0、Linux amd64、dev-foundation。同一候補・一JVMの元33と静的、XML、CRC、生counter、依存未到達をPG39382に保存。DB/実運用鍵/OS actionなし。群見積0.6/2.65/4.5pp、cap6、元行完了価格追加0。
