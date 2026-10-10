# P015-07 共通表示契約限定成果

共通headでNKを含まないtitleへ「schubert NK - 」を補い、既brandの検索/エラー/Menu titleは維持。userActionsへ閉TopBarViewModel.brandの表示を加え、全画面の既存h1/nav/username/role/Logoutを維持。既にあるNK brandと同じ値を表示し、見た目の好みによるCSS変更はない。WD-BUG-002の独立期待/修正前再現を先行保存。

最終CommonLayoutContractTest4件はF/skipped/aborted0。実Thymeleaf fragmentのみ、MockServlet request/response＋閉Map fixture、controller/business context/DB/JMS/networkなし。title/username escape、brand重複防止、2role、nav/POST Logout、共通2pagination fragmentの上下一覧・先頭/中間/末尾/0件/未検索を固定literalで確認。CSRFのsecurity integrationは未実行として分離。

PageViewModelTest8件は新しい専用sourcepath/classesでcompile/実行。対象classだけLINE33/METHOD13/CLASS1/BRANCH28全missed0。module全体やprotocolのcoverageへ補完しない。strict javac25 -Xlint:all -Werrorは成功、module全体のNullAway/SpotBugsは未実行。追加第三者jarは固定版を読み専用cacheへコピーし、主担当jar/class/targetを使用しない。最初のcommons-logging欠落は工具失敗として保存、固定POM1.3.5を補った後に仕様違反再現2件へ到達。失敗・未実行を合格に数えない。

P015-02/正式品質/実Browser/CHR/統合sourceでの必要な再検証と正式915/916対応は主担当へ残す。共通fragmentの修正・PT費は各画面へ二重配賦しない。command/実exit/各試行/coverage/hash/予実は隣接JSON、class/XML/TAPは副担当専用target又は本報告のsynthetic証跡。N/T=取得不能null。
