# 比較ゲートの承認済みcase選択 実行結果

PG45574、対象 bd8c25d09df60ac51df5050659dac3a894bb705c。期限付きのローカル合成試験は8件成功、失敗／エラー／skip各0。新PT-CHR-SYN009の固定診断を確認。正規比較JAR17物理と型付き厳格compileを照合し、選択書式6件は差分0。単一execの入口はL35/M1、対象二物理全体はmanifestの未網羅を保持。実Current/NK、全六製品451、正式計上は未了。

最初の保存ラッパーは出力にないsession行を要求し、8件の終了後に復旧が必要だった。元JUnit／execを保全し、標準CLIの読取で一session・両class CRCを照合した。試験の再実行は0。 [実行証跡](evidence/PG45574-chr-approved-artifact-selection-ordinary-eight/manifest.json)
