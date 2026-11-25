# 比較ゲートの承認済みcase選択 単体仕様

NK-CHR-001、UI264、SS355 §5、WBS-P020-01.03/2、BUG-3905／YKT-3023。GateContractValidator.validateComparisonSnapshot／validateRun／validateBaseline。承認済み24件を対象に証拠を検査し、定義違反と正規証拠の欠落を独立して報告する。

| Test ID | 独立期待値 |
| --- | --- |
| PT-CHR-SYN009 | 既存の合成fixtureの定義で最初の承認済みcaseを未登録の正常形式IDへ置換し、第一反復だけから既承認のA01証拠を外す。終了判定は失敗。24件の定義要素を観測し、定義順と第一反復のA01欠落を出す。未登録caseの欠落や第二反復・baselineのcase範囲の異常は出さない。期待値の根拠はUI264・SS355と手作業で変えた二入力。 |
| SYN001〜008のうち現対象 | 正常24、比較snapshot、既存の欠落・無効・補助、そして二treeの独立を、元の独立期待値のまま現正規工具へ適用する。 |

旧Currentや実運用の収集・コマンドを使わない。ローカル合成93資源、同じJDK・Mavenと正規比較JAR、現試験の指名。型付き前提と書式は許可sourceに限定。RDF／UI／SSを変更せず、実CHR・全体451の判定と分離する。結果は実終了、XML、execと生四指標、対象class、sourceとhashを103とmanifestで確認する。
