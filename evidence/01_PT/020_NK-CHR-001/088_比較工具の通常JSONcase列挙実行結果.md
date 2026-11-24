# 比較工具の通常JSON case列挙 実行結果

BUG-3769、YKT-2945、SS355 §4、WBS-P020-01.01/2-b。PG44218は期待2件と実際3件の差で1件失敗。修正後PG44220は1件成功。PG44222はJDK25.0.4で通常JSONの固定順と同名ディレクトリの除外、欠落ディレクトリの空結果を同一execにて2件成功。失敗／エラー／skip各0。選択した入口・並べ替え・生成lambda計7メソッドは命令、行、メソッドと2分岐を全実測。Google Java FormatとCheckstyleは正規入力2ファイル、各終了0。工具クラスの未検証範囲をrawに保持。実Current/NK比較、CHR合格、全451、正式判定IDは未成立。 [修正前](evidence/PG44218-chr-case-file-kind-before/manifest.json) [初回修正後](evidence/PG44220-chr-case-file-kind-after/manifest.json) [追加境界と静的](evidence/PG44222-chr-case-files-coverage-and-static/manifest.json)
