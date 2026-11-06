# 動画・Music表示CSS 互換契約単体仕様

NK-WEB-002/WBS-P016-25（485のCSS主担当/費用owner）。変更契機SCR010/P016-10、SCR013/P016-13、SCR007/P016-07は既prefix不変を参照し共通費重複無し。RD FUN006007/SYS006、UI222/223§6/7/235、SS313/333、BUG2350/YKT2095。製品src/.../static/css/schubert.css、Test input029/独立golden030、Python CssCompatibilityContracts各methodを対象とする。

現行publicプログラムstylesheetの動画570..587/Music635..700/900px条項とUI223を、NK製品コードを参照せず手動16rule/62property辞書へ転記した。Current CSS hash bf146326fc9fbb72474cbcc31c2fc9b860d6b9aa9b42ac350be8f0e99fe770e7、読取のみ/原本media・master/DBを扱わない。Currentのglobal audio/max-width/heightとdownloadは、Music専用selectorへ限定し同じ実効指定を保持する。現行の幅1280・16/9・max-height calc・色/枠・grid・文字/placeholder・900px一列をコード都合で変えない。Current baseline/Gate/DIF/上位正本不変更。

| Test ID | method | 事前入力・独立期待 | rule数 |
|---|---|---|---:|
|PT-STYLE-PORT001|test_001_video_page_keeps_current_1280_bound|.video-page max-width1280px|1|
|PT-STYLE-PORT002|test_002_video_frame_keeps_current_clipping_and_colors|背景#111・1px枠#2f3338・角8px・overflow hidden|1|
|PT-STYLE-PORT003|test_003_video_player_keeps_current_16_9_and_height_policy|block/width100%/max-height calc(100vh - 150px)/black/aspect-ratio16 / 9|1|
|PT-STYLE-PORT004|test_004_music_rows_titles_and_spacing_keep_current_layout|list/row/info/strongの14宣言、grid320px・padding/border・gap・折返し|4|
|PT-STYLE-PORT005|test_005_music_pair_players_placeholders_and_controls_keep_current|player/audio/pair/label/placeholder/scopedDL、Current属性と同じ36宣言、他screenのglobal audio/downloadへ波及させない|7|
|PT-STYLE-PORT006|test_006_mobile_music_and_pair_columns_keep_current_900_breakpoint|media max-width900pxのrow/song-players各1fr、Desktopと区別|2|
|PT-STYLE-PORT007|test_007_existing_prefix_is_unchanged_and_suffix_has_only_target_rules|旧CSS146682...全byte prefix不変、marker一つ、suffixは明示16ruleだけで余分なglobal変更無し|全体|

Python3.14/tinycss2 1.4.0・webencodings0.5.1をpublic PyPIからwheel SHA確認・安全なrelative展開で専用work/toolchainへ導入。087 installer/PG20698 toolchain-manifestにsource/version/hash/reproを保存、global環境・Maven依存は不変更。公式API参照先は https://doc.courtbouillon.org/tinycss2/v1.4.0/api_reference.html （取得時ページは1.5.1表示、実使用1.4.0のAPIをローカル実体と別metadata5件で検証）。parserはproperty意味やcomputed layoutを検証しないため、手動独立62値とのexact比較とviewport contextを必須とする。

別ParserMetadataの5件はnested媒体/コメント、引用符内semicolon、null/不正宣言/外部import拒否、同selector重複の曖昧拒否、manual golden全件とreadonly Current・audio継承との独立照合。これはTest工具確認でありProduct PT7へ加算しない。異常/null等はこの分離された工具contractとparserのerror拒否で扱う。CSS自体にtransaction/再送/並行動的処理はなくN/A、旧prefix/原本hash不変で共有資源を保全する。

実行: `env PYTHONPATH=/home/mini/codex/project1/work/toolchain/css-contract-parser-1.4.0/site python3 -B evidence/01_PT/016_NK-WEB-002/input/029_media_css_contracts.py product <actualCssPath> <frozenGitHEAD> <newOutputDir>`。metadataは`metadata <newOutputDir>`。Test/golden/before fixture/Git CSS/source/branch/hashを開始前照合する。旧source RED/新source GREENを別runへ保存。正常Maven packageは変更後資源に必要な一回だけ、Testを読み込まずskip、全1844 Java class bytesが旧normal20586とcode/debug完全一致か照合し、BuildをProduct試験合格へ足さない。

単体結果は7method/XML/FESaborted0、OS/Python/parser/JDK・command/時刻/source/hash/期待辞書/実際値をmanifestへ結合する。CSSはJava四counter無しnull、未測定を100に補完しない。実Browser/CSS computed値・本物media/Browser/HTTP/Root/VM/DB/鍵/native/CHR/全451はHOLDで未実施。この静的資源PTを実NK Browser受入/全UI表示保証/PGPT完了にしない。原失敗・再試験・BUG/YKT対象を結果146へ保存する。
