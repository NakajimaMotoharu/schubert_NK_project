# NK-OPS-001 静的解析の出力保全

BUG-3583／YKT-2818、WBS-G08、SS354および451のsource/run/証跡固定。対象は `tools/quality/static_report_paths.py`。独立に確保済みの作業ディレクトリと、Checkstyle、PMD、SpotBugsの実行予定引数を持つJSONの `stages` を渡す。新しい検査で使用する前に `python3 -B tools/quality/static_report_paths.py --run-directory <現在の絶対path> --plan <静的解析計画>` を実行する。

| Test ID | 入力 | 独立期待値 |
|---|---|---|
| PT-OPS-STATIC-REPORT-001 | 現run直下の3種の未使用XMLとPMDの現ソース一覧 | 真、現runの3出力先を返し、ファイルを作らない。 |
| PT-OPS-STATIC-REPORT-002 | Checkstyleが過去runの出力ファイルを指す、または相対指定 | 両方拒否。 |
| PT-OPS-STATIC-REPORT-003 | 既存レポートと、実体がないsymlink | どちらも拒否。 |
| PT-OPS-STATIC-REPORT-004 | 別名オプションを含む二重出力指定 | 曖昧な出力先として拒否。 |
| PT-OPS-STATIC-REPORT-005 | PMDが古いfile-listを指すか、現file-listがsymlink | 両方拒否。 |
| PT-OPS-STATIC-REPORT-006 | 現runを参照するsymlinkのディレクトリ | 拒否。 |

各試験は旧証跡を模した固定ファイルのSHA-256を前後で比較する。解析対象や補助JARの許可とhashは従来の入力照合で確認する。出力検査は準備時点の判定で、同時に変更し得る第三者との排他や解析結果の正当性は別の条件。
