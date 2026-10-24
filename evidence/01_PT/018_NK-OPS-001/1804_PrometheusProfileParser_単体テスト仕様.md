# Prometheus公開profile固定版parser PT

NK-OPS-001 / RD171・UI252・SS351 / WBS-P018-09主、C07参照0加算。group2032、開始fresh39残61/reset1793382075、1/3/6pp・cap10。Production f817b004781e6c32aa2d384dd12855cad7175ddcを変更せず、正常8632の全input byte照合で再利用する。1730～1731の静的8件は再演しない。

PG済みdebug/standard.yml.templateを、既準備8162のpromtool3.13.5/linux-amd64（SHA4e84296d…）の `check config --lint=all --lint-fatal <public-file>` へ渡す。syntax-only・ignore-unknown・lint抑制を使わない。着手条件は公開JSONの全key/値allowlist、固定loopback二target、file参照/認証/discovery/proxy/remote/alert/rule設定なし、binary/profile hash一致。検証は所有temp内の新規file・空環境PATH/LANGだけ、daemon/scrape/network/VM/DB/既processアクセス0。確認済み静的検証の範囲をactualサービスHOLD解除へ拡張しない。

tools/quality/architecture/PrometheusProfileParserTest の以下8件/1suite。事前fixtureは固定binaryと公開二profile、独立期待は製品parserの設定構文・strict unknown field・duration・job一意性・timeout<=interval・list型の契約。production methodをexpected算出に使わない。

| Test ID | 入力・操作 | 独立期待 |
|---|---|---|
| PROMPARSE001 | 実DEBUG profile同byte | exit0 |
| PROMPARSE002 | 実STANDARD profile同byte | exit0 |
| PROMPARSE003 | `{` | 構文拒否exit1又はlint3 |
| PROMPARSE004 | unknown_nk_field | strict未知key拒否1/3 |
| PROMPARSE005 | interval NOT_DURATION | duration拒否1/3 |
| PROMPARSE006 | 同名job二つ、targetなし | 一意性拒否1/3 |
| PROMPARSE007 | interval1s/timeout2s | 大小関係拒否1/3 |
| PROMPARSE008 | scrape_configsを文字列 | list型拒否1/3 |

各caseは30秒、timeout/signal/crash/skipをPASSへ算入しない。入力不変、実diagnostic非空、input/output SHAと実exitを原JUnit stdoutへ記録。tempの公開入力/診断だけを使用、秘密情報なし。native生成DB/サーバ/アカウント操作なし。null/所有/並行等のJava production新規変更はなく新Main0、coverageQualified=false/staticQualificationAdded=false。既counter合算/除外追加なし。

実commandは `env PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg8652_prometheus_profile_parser_host.py`、独立post8654で元XML/log/exec-session/input/source/工具/deps/hashを照合する。全環境・日時・branch・exit・hashは各manifestと1805に記録。着手時8 UNRUN。障害発見時は修正前BUG/YKTへ起票。正式1964/53・原190新受入0・工数null・QA051final・whole451未完、F03Root11/actual操作HOLD不変更。
