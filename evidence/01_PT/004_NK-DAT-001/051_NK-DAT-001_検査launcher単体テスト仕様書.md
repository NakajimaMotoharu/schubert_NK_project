# NK-DAT-001 検査launcher 単体テスト仕様書

RD DAT-009/OPS-009/FIL-006、UI212/241/251、SS343 §6.8/341 §12/342/352、QA-046/UIC-006/SSC-049/PG-D-144。非秘密入力境界、InspectorLauncher main、固定receiptを対象。受渡し元のroot所有設定file検証・親OS lock/backup実体・全朝batch・実root配布は別gate。

## 1. 独立期待値とfixture

期待はliteral key/ASCII byte/UUID/UTC時刻・不変集合、明示0/10/50/70から作る。実factoryは保持root拒否を確認し、正常/警告/故障matrixはpackage内の限定operation factoryへ注入する。defaultはInspectorApplicationへのbound methodであり、任意runtime plugin/commandを公開しない。既存049/050の実file/JDBC/resource PTを回帰する。public mainと実Java subprocessも呼び、mainのJVM exit0を業務成功と解釈しない。全secret・raw exception値は出力しない。

## 2. Test ID

| ID | class/method | 入力/操作・独立期待値 |
|---|---|---|
| PT-DB-INBOX-221 | InspectorLaunchConfigurationTest.validConfiguration | 5 canonical値と無関係OS変数。正しいSettings/固定InspectionRun、元mapを保持しない |
| PT-DB-INBOX-222 | 同.missingUnknownAndArguments | 全必須欠落/null/空、argv非空、未知namespace/大小文字aliasを70用固定例外、無関係envは無視 |
| PT-DB-INBOX-223 | 同.scalarBoundaries | 長さ上限/超過、NUL/CR/LF、root/URL/UUID/cutoffの非canonical・範囲/精度不正を拒否、元値を例外へ含めない |
| PT-DB-INBOX-224 | 同.versionAndSnapshotContracts | CSV空要素/重複/不正version/過長、1/16byte境界、入力変更非伝播、version集合返却不変、record redaction |
| PT-DB-INBOX-225 | InspectorLauncherTest.successWarningAndFailureStatus | SUCCESS/WARNING/TIME_LIMIT/INTERRUPTED/STORAGE_FAILUREを明示0/10/50へ写像。固定run/settingsをoperationへ渡す |
| PT-DB-INBOX-226 | 同.expectedFailuresAndRedaction | config/credential/暗号構成70、storage50、cause/message秘匿。予期外runtimeを成功へ変換しない |
| PT-DB-INBOX-227 | 同.nativeFactoryFailure | default factoryと実LinuxでRW/非専用root拒否70、missing root50。合成metadata正系を実systemd正系と主張しない |
| PT-DB-INBOX-228 | 同.receiptAndOutputFailure | exact ASCII receipt1行、出力stream故障を固定例外、余分な設定/状態object/stackを出さない |
| PT-DB-INBOX-229 | 同.nullContracts | args/env/factory/output/戻り値のnull契約を拒否、NPEを正常扱いしない |
| PT-DB-INBOX-230 | 同.mainAndFatalHandler | 実mainの不正argsはreceipt70、公開Thread handler APIへ合成例外を渡してstderr固定文のみ、元handler/streamsをfinally復元 |
| PT-DB-INBOX-231 | 同.concurrentInvocations | 64独立run/settings/出力・faultを並行処理し混線なし、factory設定不変 |
| PT-DB-INBOX-232 | 同.actualJvmEntry | 実Java subprocessで不正args/env欠落のreceipt70/JVM0、stdout exact・stderr非秘密、wrapperとは別の契約を確認 |

## 3. 正式gate・証跡

421の固定JDK25/Maven/m2/OS。探索後source commitを固定してroot clean verify、全Java line/method/class/branch100%、NullAway/Spotless/Enforcer/SpotBugs PASS、failed/error/skipped/flaky/not-run0。052・evidence/inspector-launcher/manifest.jsonへTest ID・日時/OS/tool/branch/source/command/exit/期待・実際/coverage/BUG/SSC/hashを保存。新collectorの独立method inventory負canaryと全scope同run/source/hashを必須とする。systemd/scriptは018 NK-OPS-001へ別追跡し、合格件数を二重加算しない。
