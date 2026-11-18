# CHR-A01 承認済みログインタイトルの比較単体仕様

NK-CHR-001、ArtifactComparator.compare、WBS-P020-01.02/2、BUG-3314、YKT-2699。RD SYS-001、UI264 §5、SS355 §8、QA-045/UIC-005/SSC-074。Currentの固定artifactにある `/title` と、承認済みの `schubert - ログイン` / `schubert NK - ログイン` を独立期待とする。tool/fixtureの出力から期待値を求めない。

| Test ID | fixtureと操作 | 承認定義による結果 |
|---|---|---|
| PT-CHR-DEF017 | 24件でA01のタイトル差分を保持し、A01のDIF-001観測だけが欠落。他caseのDIF-001は保持。 | 不合格。A01 titleの要求、不登録差分一件、DIF-001自体は別caseで使用済み。 |
| PT-CHR-DEF018 | A01のDIF-001観測のpointerを存在しない正規JSON Pointerへ変更。 | 不合格。承認対象との不一致。A01 titleは未登録差分として残る。 |
| PT-CHR-DEF019 | A01のCurrent titleを別の合成文字列に変更。 | 不合格。Currentの固定期待は不一致。登録済みtitle差分として消費しない。 |
| PT-CHR-DEF020 | A01のNK titleを別の合成文字列に変更。 | 不合格。NKの固定期待は不一致。登録済みtitle差分として消費しない。 |

元144通常試験の正fixtureへA01の承認観測を一件追加して、全24 case／承認済みDIF 16件の完全な正例を維持する。固定観測数と元DIF-001の全体未使用アサーションは、この一件の独立期待を反映する。元のDIF、基準Current 27ファイル、HTTPや実NKの捕捉は維持。所有する合成TempDir内のJDKファイル操作だけを実施する。並行・再送・実ログ、実ブラウザは比較関数の当該境界の対象外。全148を一回で確認し、指摘・F/E/S/未実行と同sourceの生coverage、別のCLI正常分岐の不足は結果文書へ記録する。
