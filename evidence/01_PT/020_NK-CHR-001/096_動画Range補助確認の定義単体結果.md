# 動画Range補助確認の定義単体結果

NK-CHR-001、PT-CHR-DEF-MEDIA001、BUG-3813／YKT-2971。修正後工具source `18f527f0d1e0312a7c6f4d406b819c4d42cc4fa4`、製品Core `8e2a6b055c45f9f868433c73174b87bc72972d77`。合成の公開定義だけを使った。

修正前は選択1件が失敗し、四つの欠落・置換条件すべてで診断が空だった。修正後の正規JARはMaven終了0。既定の合成範囲に新1件を加え、工具試験89成功、失敗・エラー・スキップ0。現単一execの対象はvalidatorと結果recordの二物理。行561、メソッド73、クラス2、分岐303、命令3,139は未到達0。書式とCheckstyle指摘0。正規Spotlessは変更二ファイルを選択し、修正要求0・キャッシュ0。

初回の再現準備は試験ファイル指定漏れでjavac終了2。実際の再現終了1と区別した。正規JAR作成時のSpotlessは選択数を出力しなかったため、選択数を示す正規の明示検査を別に取得した。製品試験、実Current/NK取得、正式受入の加算は0。

入力、commands、各exit、XML、単一execとraw、公開仕様のSHA-256をmanifestに保存した。 [PG44950](evidence/PG44950-video-observation-definition-gate/manifest.json)
