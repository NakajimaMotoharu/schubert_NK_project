# 固定source hygieneの意味保存是正

NK-OPS-001/F03、SS352/354・411/451、BUG1313/YKT1079。まず531 wildcardの展開候補をstagingし、JDK25公開Compiler APIの実symbol bindingで採取する。import木以外のAST/元body literalは変えない。通常package/type-on-demandとstatic-on-demand、継承static member/入れ子type/同名/未使用の独立小fixtureで展開と再compile/binding同一を確認する。元645 report/2217PMDは保持。将来の113同時宣言とTAB1も同群の別段階とし、確認前に修正済としない。

PT-F03-3686-001：正/負の独立Java小fixture、literal期待import集合、欠落/誤symbol/不明typeは拒否。002：全849元source・hash固定、moduleごとの真正Maven compile classpathからbindingを解決、candidate以外の既sourceを上書き0。003：候補の解決binding/業務木/literalと元を比較、同一bindingを保証してから定形bulk反映。004：fixed GJF/Checkstyleで全rule適用、違反0未達は未達、rule除外0。005：変更群をまとめた必要一全体/全scope、同source native CRC/line table/Current baseline/traceを独立確認。line/method/class/branchは全100維持、未達を完了としない。

群subset開始見積り低0.5/標準2/高5共有pp、scopeは機械展開/独立binding proof/固定style確認まで。共有K01全体・VM native/個別P業務変更はこのsubsetへ二重配賦しない。複数P参照の実費配賦はnull、F03全完了予算ではない。計測eventの実消費/残見積り・失敗原因を保存。先にreadonly候補を作り、Main反映前に不明bindingを解消する。
