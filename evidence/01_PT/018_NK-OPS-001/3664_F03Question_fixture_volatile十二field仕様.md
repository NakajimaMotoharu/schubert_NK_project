# F03 Question fixture volatile十二fieldの個別可視性確認

WBS-F03、411§9/10/451/SS351352。原1/3/7pp cap9。current85 subset346raw/271分類/未分類75のうちQuestionControllerTest.FixtureのAvoidUsingVolatile12を対象にする。2076は別の三画面fixtureの十field・並行write0であり、この十二へ転用しない。

当scopeはTest source静的データのみ。volatile個別scalar/String/function-referenceはTestの入力control publicationで、Productionの複数field atomic transitionを実装/受入するものではない。全十二decl/全writeとactual method/owner・並行phaseを独立ASTで照合する。外側f.field writeは所有new Fixtureのscope内だけ、compound RMW/reflect mutationがあれば未証明とする。

二つのpool並行Testはcontrol setupを最初のpool.submitより前に完了し、明示f.fieldを書換えない。他方Fixture.accepting/acceptanceMvcはverifyNoTransaction=trueを設定する。並行側がacceptingを呼ぶため、bare write0とは認定しない。このbooleanの書込みは全てtrueの一方向・冪等設定に限定し、他十一controlは並行phase中read-only。複数fieldの同時切替/atomic snapshot/実runtime coherenceやlivenessを保証しない。Test所有/期限/cleanupの動的合格へ換算しない。

既QuestionController wholeの認証/session/DB/実wire/Root/native動的HOLDは不変、新fixture・Test/PMD実行・元処理再演0。公開既source一つだけを読取り、4guard型/保護2file/Root2Testへ範囲を拡げない。既source/原347 XML/現構成346と全metadata hashを保持、コード・規則・抑制変更なし。

期待は検証成立した十二の個別非該当理由だけ。前提不足は未分類のまま、Map62/reflect1は保持。独立ASTとwrong field/missing owner/concurrent nonmonotone write/RMW/decl欠落等のmetadata反例で確定する。全scope/source/run/正式1964-53/unique430/whole94/工数null/全HOLD/451は不変更。


## 追加発見・検査範囲の分離（BUG2432/YKT2177）

原210の両phaseにTimeUnit.SECONDSがあるという補助guardは第二phaseの無期限job.getを検出し終了1、原本文/guardを22468へ保持。code/Testは変更せず、v2はこの不具合をopen metadataとして保存し、volatile可視性とTest wait品質の状態を分けて集計する。有限wait条件の免除/正常化ではなく、全Test/globalF03/動的品質は不合格・未受入のまま。元見積/開始event不変、追加発見費splitnull。原controller/Testを起動せず、BUGは後続の許可済PG/static scopeで是正・実Test再資格はHOLDの範囲を維持する。
