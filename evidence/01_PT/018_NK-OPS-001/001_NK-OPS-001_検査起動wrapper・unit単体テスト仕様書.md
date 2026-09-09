# NK-OPS-001 検査起動wrapper・unit 単体テスト仕様書

RD OPS-009/ENV/SEC、UI212/251/252、SS341/342/343 §6.8/352、QA-046/UIC-006/SSC-049/PG-D-144。専用wrapperとbase/previous選択unit雛形の部分PT。全OPS Programや実unit/ITの完了ではない。

## 1. Fixture・網羅方針

InspectorDeploymentTest（API PT module配置、Program所有はNK-OPS-001）が実sh、ShellCheck0.11.0、systemd-analyze259.5を呼ぶ。wrapperは作業一時directoryへrenderし、固定fake Javaが公開receipt/終了codeを返す。実Java mainの負例も接続。unit検証は一時unit path・stub PostgreSQL dependency・実在する検証専用ExecStartへrenderし、host daemon/設定/credentialは変更しない。

Javaの4指標は全100%。shellは引数/placeholder/child exit/case4status/defaultの全判定とstatementを独立matrixで検証し、traceとsource行対応を証跡化する。class/methodはshell/unitでは非該当でありJava値を流用しない。unitは全directiveと4 previous profileの設定値/重複禁止/固定source pathを独立表で検証する。実root credential配布・timeout/TERM・親OS gateをstatic verifyで代用済みとはしない。

## 2. Test ID

| ID | InspectorDeploymentTest.method | 事前条件・入力/操作・独立期待値 |
|---|---|---|
| PT-OPS-INBOX-001 | renderedShellCheck | template全placeholderを固定値でrender、POSIX sh/ShellCheck error/warning0、source hash保持 |
| PT-OPS-INBOX-002 | statusMapping | exact receipt0/10/50/70＋JVM0だけ対応exit。JVM非zero/異常signal相当はreceipt0でも50 |
| PT-OPS-INBOX-003 | malformedReceipts | empty/未知prefix/code/余分text/space/LF/CRLF/改行なし/複数行を50。shellの末尾LF消去で誤受理しない |
| PT-OPS-INBOX-004 | argumentsAndPlaceholders | 引数1/複数/未renderは70、child実行前に停止。未知placeholderは配備不合格 |
| PT-OPS-INBOX-005 | realMainBridge | actual Java mainの負入力をwrapperへ接続し、JVM0＋receipt70→OS exit70、stdoutへraw値を出さない |
| PT-OPS-INBOX-006 | baseUnitAndSyntax | 全base directiveを独立期待表と一致、read-only/専用identity/30min/no-auto-SIGKILL/正しいwrapper、systemd-analyze verify成功。実unit起動ではない |
| PT-OPS-INBOX-007 | previousProfiles | base3 credential＋optional0/1/1/2の4profile、固定ID/pathと重複なし。空fallback/省略source/広いcredstore検索なし |
| PT-OPS-INBOX-008 | releaseClasspathAndIsolation | API jar＋runtime lib classpath、PG driver runtime依存、固定JVM/native/UTF8/UTC/heap flags、任意command/eval/env上書きの禁止、release layoutとの追跡 |

## 3. 正式証跡

root clean verifyの8 Java testとして実行し、002・evidence/manifest.jsonへ日時/環境/source/branch/command/exit、各IDの期待・実際、sanitized script trace/静的解析結果、unit profile対応、source hashを保存する。collectorは全8完全method名とfail/error/skipped/unknown/重複を検証し、他scopeと同run/source/hashへ束ねる。既存24 DB部品220 PTやbatch29 PTとは重複加算しない。PGPT/IT/ST完了を宣言しない。
