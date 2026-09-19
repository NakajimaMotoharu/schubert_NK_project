# Animationメニュー・一覧template単体テスト仕様書

NK-WEB-002/SCR008/009、animation.html/animation-list.html/CSS/WebMvcConfiguration、FUN006/AUT/TST、UI222/223/235/264、SS313/352、PG205。正式21で8PT合格、実行詳細は012とmanifest参照。AnimationTemplateTestの8methodを次へ一意対応。

| Test ID | method | fixture/操作 | 独立期待値 |
|---|---|---|---|
| PT-SCR-046 | animation046Menu | 両role・15/4/true/20、0/0/false/0 | Current Animation/title/h1、3card順/文言/URL、Opening falseでもcard維持、共通操作/Logout |
| PT-SCR-047 | animation047MainRows | 3main/2sub・API順、実resolver | subtitle5本、rows3、parent対応、SUBTRACK2link/placeholder1、metadata保持 |
| PT-SCR-048 | animation048OvaRows | 4OVAをliteral順 | OVA一覧/title/4本、title/category/path/MB/URL、main行なし |
| PT-SCR-049 | animation049EmptyAndMaximum | 両一覧0/50・main25pair | 空section/空文言追加なし、全50/端点・順序、切捨てなし |
| PT-SCR-050 | animation050MegabyteRounding | 1/996147/996148/1048576/1572864/10485760byte | Current式を独立算出した0.0/0.9/1.0/1.0/1.5/10.0 MB、Locale.JAPAN |
| PT-SCR-051 | animation051EscapingAndCsrf | title/path/username特殊文字、両template | escape、注入要素/inline handler/秘密contextなし、LogoutだけCSRF1 |
| PT-SCR-052 | animation052CssAndViewBoundary | 独立Current CSS宣言、resolver名 | 7desktop＋900px1規則の全値/順序、2view許可・unknown拒否 |
| PT-SCR-053 | animation053ConcurrentRendering | 64独立actor/model/CSRF・共有resolver | 各DOM/値/CSRFに混入なし、公開count trace |

model/form null・group不整合は015016のPG204と組み合わせ、template全条件/反復を独立DOMで確認する。CSSの文字列検証を実Browser screenshotとは呼ばない。Productionと同じprojectionで期待値を作らず、Current/UIのliteralを転記する。Java全4coverage100%・静的解析0、既存Menu/Error/Scenario/Search/script回帰。再送は純粋render反復/並行だけでMQ再送の証明ではない。

実行command/日時/OS/JDK/branch/commit/exit/input/expected/actual/coverage/BUG/SSC/path/hashは012結果・manifestに保存。raw token/CSRF/HTML/credentialをGitへ保存せず公開traceだけ。実HTTP/実MQ/実Browser/実NKgate/PGPT・IT/ST未完了。
