# G07既存位置不一致一件・限定診断結果

2026-10-25/group2122/WBS-G07、仕様1890。Production source64446不変更、歴史scan content05d73a7974da8df92228160b96d91e7a006768f3/sourcefb9と現在PTを合算しない。元finding40,086・公開由来根拠31,707・未分類8,379は不変更。追加したのは「報告行が公開ソースhash metadataである」という独立証明一件で、実captureの追加誤検出認定は0件。

| 公開manifest（evidence/provisional配下） | 結果 | SHA256 |
|---|---|---|
| PG9296-g07-one-range-diagnosis-v1 | 公開reported tuple一、Git source/metadata行/binary二rule一致を確認、capture未確定を保持 | e1de541969ec807893a234c5a4e3fd23f74c4bf162728ab1c5582b68682615cf |
| PG9297-g07-one-range-post-v1 | 独立Git blob＋手組みASCII JSON行/原snapshot・8metadata反例、追加false positive0 | 884500a8231d88a2aa7bb08e3d4874c570a7b2e9d6d5cf703d816e210f9a8bbe |

元tupleは公開PG8634-api-web-custom-payload-host-v1/manifest.jsonのlinear-client-secret/1680行、input SHA5f09c33d46e0a3a9de6ab0259a0fd4c110e2aff7c95570f9cc6ed4cfebbeafac、元multiplicity1。snapshotと原Git blob byteが一致し、LF/Unicode改行のずれは0。同報告行は公開Test source path→その全文SHA-256を一つ書いたJSON memberで、sourcef817b004781e6c32aa2d384dd12855cad7175ddc/ServiceDeadlineArgumentTest.java/Git object4f83b36b1d2a35af220312d02ba5157efc1bc15fを独立hashして全行を再構成できた。公開blob由来SHA7d86c386f2583fd4ae26d5e5d3fe0f3d7e402087837da57a785b7cb4b7654124はsource artifact hashであり、秘密候補やその単体hashではない。原capture値/そのhash/周辺contextは保存・出力0。

元default.tomlはextend.useDefault=trueだけ。既scanと同SHA88f91962のpublic vendor binaryから選択二ruleのTOML stanzaを読み、既pin済みv8.30.1 tag config SHAe163e53bとのid/regex/entropy/keywordsがgeneric-api-key・linear-client-secretとも一致した。byte/parity読取だけでscanner data modeは実行しない。CLI metadata確認としてgitleaks --help一回/exit0は実行済み、manifestのscannerExecuted=falseはdir/git/stdinのscan invocationが0という意味で、binary metadata processも0という意味ではない。元全scan/再decode/archive/新target/私有raw/VM/DB/鍵/Rootへの操作0。

全原文に当ruleを適用したmatchは0。一方、RAMだけの独立synthetic4 vectorで、32hex文字列はmatch、64hex全体は非match、32位置で文脈を終えたものはmatch、非linear keyは非matchという境界差を確認した。ただしこれを原実captureと推定しない。[当versionの公開一次資料](https://raw.githubusercontent.com/gitleaks/gitleaks/v8.30.1/sources/file.go)には固定buffer読取と境界延長の処理があるが、この原runの実断片終端は公開証跡から再構成できていない（source raw file hashも未取得null、実断片attestationではない）。原rangeが公開metadataであることと、元scanner captureの正確な対応が証明できたことは区別する。

公開source directoryのWeb fetchはrestricted URLで取得できず、そのURLの再試行/別経路取得はしなかった。拒否PT/実VM/Rootの保留を解除したり、断片境界の推測で期待値・findingを変更しない。NO_EXACT_CAPTURE一件は未分類のまま、他8,378も継続未分類、actual secret数null/全G07・451未受入。新BUG/製品PT/新Main/正式受入増分0。独立postはcapture捏造/false-positive増加/unknown secret0化/scanner再演/別行/別object/余剰Secret出力/拒否URL再試行の8反例を拒否した。

再現commandはPYTHONPATH=tools/quality:tools/quality/vm/050_s1:toolchain/pyflakes-runtimeのpython3 -B tools/quality/pg9296_g07_one_range_diagnosis.py（新規OUT専用）とpg9297_g07_one_range_post.py。実source/object/config/binary/hash・行の構造はmanifestへ、未実行scanner結果をPASSへ加算しない。OS/tool群は既host source環境、製品source/compile/execは変更・起動0。

開始.25/.5/1pp cap1固定、fresh61→62（2026-10-25T02:17:48+00:00観測）共有1pp・専有N/T/工数null、usage8f25f8597b2ce39f3e5ffcf9887cefd0aaaab8425952e39c97b856af5f0fcab3は欠測0補填なし。元90下限87・不明2/正確null/80大型抑制・保全2、次は下限＋短群cap＋保全2<=90の場合だけ。元/v4/v5・879新ID/新Main42/必要既存7・正式1964-53/原190新受入0/QA051final/HOLD/原本等保持。公開位置証明一件を工数率や新規受入へ換算せず、通常保存後も許可範囲の短品質工程へ継続する。
