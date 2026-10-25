# NK-PRO-002 ページ境界・実行結果（限定3件・独立照合済み）

2026-10-25追記：静的v2 manifest `evidence/provisional/PG9666-pagination-static-v2/manifest.json` SHA-256 `41807eb5d29a989424939246359f8eb7f9162bd03c7fbc4d1f2bd8932546de08`、独立trace/quality post v2 `evidence/provisional/PG9668-pagination-trace-quality-post-v2/manifest.json` SHA-256 `9db0e573444f6fd72649fd68efcddfe8e6d15eedb1e0d2069efbb9d7525bd445` は各実終了0。原静的v1のMissingClass18と終了1を保持し、全六moduleへ現1843Main class/六current jar/外部依存のhashを指定して再解析し、各BugInstance/MissingClass/Error0を別XML照合した。新Test PMD/Checkstyle各0は同sourceの原v1内の成功subcheckのみ参照し、v1全体を成功へ変換しない。

追加postは新3methodのJDK parse-only AST/normal class annotation/descriptor/引数0/仕様ID/実XMLとの一致、旧1910Test class不変＋追加1class、Main965/Test825/Java1790、元Mainの原主担当/費用担当P002-02を確認した。通常Test宣言5625は旧5622＋新3であり実行済み件数ではない。485原941artifactと9546追加候補だけのsourceRowsを混同したpost v1はassert終了1・成功manifestなしで保持（BUG1755/YKT1506）。v2は原正本から担当取得、現Main byteは別current hashへ束縛し、欠落/重複/owner誤り/cost誤り四反例も確認。初回unused importの実行前lintとpost lookup失敗は工具手戻りとして別記、製品試験失敗ではない。

BUG1754/YKT1505・BUG1755/YKT1506は工具scope検証済み、修正commitのremote照合待ち。新3試験成功/1suite、四counter未達、正式1964PT/53scope・17/190・工数null、旧64446全監査HOLD/新3154全監査未実行は不変。QA053は利用者から「通知はもう存在しない」と回答受領、情報照会を終了し拒否対象未特定/HOLDは保持。以下は原実行時の記録で、現在状態は本追記を優先する。

対象source3154be39380de4771111f859ffb8315420274b0a、branch dev-foundation、主WBS-P002-02、群2199・開始.5/2/5pp cap10。006の新PAGE001～003は正常compile後に専用JUnitで実行し三成功/一suite、failed/error/skipped/aborted0を独立照合した。PG9660六module compile/packageは終了0/実PT0、未実行の旧全回帰をPASSへ算入0。

| 証跡 | path（各manifest.json） | SHA-256 |
|---|---|---|
| 正常六compile | ../018_NK-OPS-001/evidence/provisional/PG9660-pagination-six-compile-v1 | f2ae182bb3a88eff78542ce0c18f3a497263aaabb7ed7fdbea5237a9ab467c2c |
| 新三PT原終端 | evidence/provisional/PG9662-pagination-boundary-host-v1 | c5dfb7e4137c0c96833bcba4a3a3c6ec5cba04a54b3134d13b7395d808cbc19e |
| 独立XML/source/CRC/post | evidence/provisional/PG9664-pagination-boundary-post-v1 | d12d686512ce45599f7a9eaa89d03560a7c579aaa8c3e5036b9de2a641510959 |
| 静的gate v1不合格 | evidence/provisional/PG9666-pagination-static-v1 | 8d84b114236c23040c081547441776cc038835f85ca60398da499a0b4b4df6d4 |

当runのPayloadSemanticValidator全class countersはline72/315、method11/38、class1/1、branch22/197。missed243/27/0/175を隠さず、旧execとのunion/除外0、四100/Program完了ではない。新三caseのみのJUnitXML/summaryを独立post公開folderへコピーしhash一致、JaCoCo execは自己作業領域で保全。全1843Main classは旧64446正常compileと同byte（比較証拠のみ、旧PT転用0）。Testはdirect typed component fixtureでありnamed業務pipeline/native/DBの受入ではない。

静的v1：新TestのPMD/Checkstyleは各指摘0/処理error0、六module SpotBugs BugInstanceは各0だが四moduleのMissingClass18でwrapper実終了1。根拠BUG1754/YKT1505、旧M2 sibling jarへ解決するclasspathが原因。ルールや不明をPASSへ変えず、原reportを保持して正しいcurrent入力で是正する。実PT三件はsource不変更のため再実行せず、工具是正を新PT件数へ加算しない。

JDK25.0.4/Maven3.9.12/JUnit1.13.4/JaCoCo0.8.15/formatter1.36.1/PMD7.28.0/Checkstyle14.3.0/SpotBugs plugin4.10.4.0。正確なcommand/環境/時刻/OS/exit/hashは各元manifest/stage safe receiptとlauncher stdoutに保持。Normal compileの外部Spotless/JDK Unsafe deprecated通知はcompiler lintや製品違反と混同しない。Source/Main/旧台帳/Current/stash/原本/鍵/既native保全物に変更0。

正式1964PT/53scope・17/190/工数null/QA051final/QA053具体情報未受領/旧64446監査1HOLD・新3154全監査未実行/G07歴史残4493/全actualHOLDを維持。静的是正・当source trace/evidence結合/本群closeはまだ未完了。
