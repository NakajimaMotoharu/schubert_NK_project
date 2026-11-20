# F03 Cleanup終端Repositoryの現候補型付き静的検査

WBS66第2窓82行 `WBS-F03/2-2`。製品Core `517a23cddc9f3883550942f6fa90a4256ef39b73`、PG40748。PG40744で変更した物理class6件を直接採取し、PG40742が参照する通常成功PTの6件とSHA-256を照合した。SS352・354、SS332・SSC199およびSS331・341・SSC201、NK-BAT-001、PT-OPS-CEXEC001／CTERM006～009に対応する。

| 検査 | 実結果 |
|---|---|
| SpotBugs 4.10.4、max・low | 終了0。ClassStats 6/6、指摘・処理エラー・欠落class 0。 |
| PMD 7.28.0、元ruleset、Java 25 | 終了4、生48、処理エラー・抑制0。各違反座標をPG40524から行移動に照らして照合し、同一箇所48。手動判定24、未分類24。 |

現行の行座標を使い、通常参照とその進捗sealの24指摘を次の根拠で非適用とした。ソースのSHA-256、座標と列は生XMLへ対応する。

| PMDルール | `references` | `progressSeal` | 適用性の根拠 |
|---|---|---|---|
| CloseResource | 284・292（各1） | 371・380（各1） | 取得したResultSetを内側、Statementを外側のfinallyで同一instanceに対し一度closeする。nullは未取得扱い。借用Connectionの所有は移動しない。 |
| AvoidCatchingGenericException | 314・326（各2） | 385・396（各2） | bodyのRuntimeExceptionとErrorはprimaryとして記録して同じinstanceをrethrowする。通常値への変換や未知例外の握りつぶしはない。 |
| AvoidCatchingGenericException | 321・333（各2） | 392・403（各2） | 資源close時のRuntimeExceptionとErrorをSQL例外とともに有界に捕捉し、SS332が定める例外の優先順位を `JdbcResourceFailures.replace` で判定する。 |
| DoNotThrowExceptionInFinally | 317～325・329～337（各1） | 388～395・399～406（各1） | cleanupの例外はprimaryなし、又は既知SQL primaryに未知cleanupが続く場合に限り再送出する。その他はprimaryを維持し、未知primaryのsecondary報告は固定例外を使用する。 |

`read` と `readRejected` の各12件は今回の手動判定に含めず未分類のまま保存した。PMD終了4を保持する。PG40742の整形／Checkstyleと既存通常PTは証跡を参照し、追加の動的試験およびcoverageは実行していない。F03の全6製品と全451、QA-056/057の範囲は集約判定に未反映。正式受入加算0。

- [実行manifest](evidence/PG40748-f03-cleanup-terminal-current-typed-v1/manifest.json) SHA-256 `31119851e87b8fadca786f92986caddfbcf40ef81093a21409025aaf9efda8e9`
- [SpotBugs XML](evidence/PG40748-f03-cleanup-terminal-current-typed-v1/spotbugs.xml) SHA-256 `be11be60244cfd873b0628f31909e613d443ab67671f9161336abb8e8d241bb7`
- [PMD XML](evidence/PG40748-f03-cleanup-terminal-current-typed-v1/pmd.xml) SHA-256 `8ed126b70c7735aeb42874295187f1ef6bf51d7dd5f2332f250e32e2b9803b2a`
