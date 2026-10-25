# G13 明示case行候補・初回失敗とv2是正仕様

2026-10-25 17:40 JST、2183継続/BUG1752/YKT1503、Production64446不変更。初回producer9598 manifest538aedc37867bbc02c373dafde7155c77383c711ec51fb0f17786b123fdd1183は未資格のまま保全。post9600元session67588は終了1、手書きheader vectorで期待[1870]に対して[18,1870]を返す誤りを検出、成功manifestはない。動的製品PTの失敗/安全拒否ではなく、公開sourceコメントの独立metadata工具の不備である。

初回producer SHA cba41c2ee125992f02002c321a4875c95adfae1deb223dbac6eb91b81cd5beed、post SHA8b0074342a9cb6bae2617e774bbe9da934c6bb7c56d7e0297d0766bf14082b63と全候補を修正前commitへ保存する。原1946は固定し、その仕様参照の意味を次のv2でより保守的に具体化する。開始.5/3/8pp/cap10は不変更、失敗・再試行/tool是正費を新規製品成果/再認証へ付け替えない。

## v2の根拠と範囲

Javadocの先頭に明記された三/四桁の仕様番号又はslash区切りの仕様番号chainだけを採る。例「1870/APISTOP001..018」は1870、「1880/1882 WLCLOSE001..004」は1880/1882。通常Javadocの行頭asterisk/空白は除く。日付/番号範囲/任意本文中の数字/case末尾は仕様参照と推定しない。明示prefixのないsourceはglobal candidate又は未対応のままで、oracleや受入を認定しない。

producerはanchored prefix grammar、独立postはcomment/classを字句分離してprefix数字chainを手で読む別実装とする。初回手書き反例を変更せず、range/dash/全角範囲/date/五桁/本文/実class body/複数参照の反例を追加する。両source/全5622候補に適用、既metadata/hash/元corpus1188/他分類guardは保持。旧v1のfalse/unknownを正規合格へ上書きせず、影響のあったdocref/候補行数を報告する。新v2の独立post実終了0/全候補差分/全対象是正又は非該当/再発防止とcommit確認前にBUG/YKTを閉じない。

対象class/JUnit/VM/Root/native/DB/私有raw/鍵/配備/拒否未特定操作は実行0/HOLD維持。既17/190/正式1964-53/工数null/QA051final/actualHOLD不更新。通常是正後も独立PGPTへ継続し、fresh現在窓残10以下等で保全する。
