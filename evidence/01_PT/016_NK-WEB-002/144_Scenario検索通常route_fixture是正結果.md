# Scenario検索の通常リンクfixture 是正結果

BUG2349/YKT2094、仕様136追補/PT-SEARCH-DOM001..008。元Testのsingular /scenario/17#entry-9 はUI221 SCR007/SS313の /scenarios/{id} と不一致だった。Production controller/ViewModelもpluralで、製品修正/上位変更は無し。Test resultRow入力と005expectedの二literalだけを正本へ修正、元source c0f5fefa9/PG20620は改変せず保持する。旧8成功はechoされたfield値の測定事実であり、通常routeの正しさを証明しなかったことを追記する。

修正source 51d5defeca20d873e12a45dd3aa3c4d4add4d6fa、PG20680 compile0/PG20682 raw2各JUnit用途非該当/適用0/CS0。PG20684全8/FESaborted0・22DOM/strictpost0、manifest evidence/01_PT/016_NK-WEB-002/evidence/PG20684-search-route-corrected-eight-v1/manifest.json SHA256 ada1ccbb2a3c97b3ca63dc659a7f0ba0294d0957764cbe588093b78f09d77ae9、同source/input/OS-JDK/command/time/XML/実DOM/終了を結合。全DOMにsingularhrefが無く、現Testのplural2箇所/正本route/新Scenario fixtureを独立照合する。直近六Testの元検索二箇所以外にsingular route無し、新Sceneもplural。期待値はコード都合ではなく既承認routeへ是正、独立expectedとsourceはともにGit固定する。

これはchanged wrong-oracleに必要な回帰であり既成功の確認再演ではない。旧新8は同TestIDとして一度だけ数え、新PT加算0/新Source資格0/新受入0。formal/Current baseline/全451/実HTTP/Browser/Root/native/CHRは更新せず。補足JMS/Menu候補PG20670は原whole証拠があるためProduct再演0、追加成功や費用の重複計上0。
