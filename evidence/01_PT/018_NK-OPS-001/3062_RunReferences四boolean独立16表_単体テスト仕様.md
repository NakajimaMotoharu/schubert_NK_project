# RunReferences四boolean独立16表 単体テスト仕様

2026-10-31 / PG-D979 / 群3393予定 / 主WBS-P017-12.01、file責任P01712は親参照/追加費0。開始0.5/2/5共有pp cap10固定/used51。Production6b53/normal14216不変更。対象Main `RunReferences` 全文は四primitive booleanのimmutable recordだけで、repository/lookup/原本/intent/permit/DB/OS/native・業務完了操作を持たない。

SS331§3.12の四非null列/不存在consistent=true、既recordの「四falseは不整合projection」、三presenceのORと固定redacted診断を内部単体契約として検証する。SQL/DDL/真のsnapshotが誤projectionを返すことや、rawflagsだけで削除/親完了を判断できるとは主張しない。保持したDB fixture/HOLDのcaseを抽出/差替えせず、新しい独立data-only品質fixtureを作る。入力fixtureは明示16行（各四bit一意）、許可15/拒否1、presence falseは唯一0001、presence trueは他14行をliteralで固定。expectedにproduction methodを使わない。

- PT-OPS-REF-FLAGS-001：全16tupleのconstructor正常/不整合、四getterと固定例外message。
- PT-OPS-REF-FLAGS-002：許可15tupleのanyReferenceを独立literal列と比較、consistentだけではpresence=trueにしない。
- PT-OPS-REF-FLAGS-003：許可15tupleのtoStringは固定redacted literal、true/falseを表示しない。

primitive引数のnullは型上入力不可で、boxing nullを使ってcompiler/JDKのunboxing NPEを人工実行しない。新しい外部仕様は追加せず、JSpecify/NullAwayを含む固定current normal/static資格を参照する。品質fixtureは `tools/quality/architecture` の明示独立oracle domain、normal856source/5786普通@Test宣言とは別、countを混ぜない。Production sourceは全byte不変更。

SourceFile全一classを当execのSDK line/method/class/branchで測定し、四100/全分岐/独立Python16表照合/四held六native zeroを確認。元15974の部分Source proofはbyte凍結、新一execで当一Sourceだけ置換し履歴保存、coverage unionなし。前groupのproxy/SQL/core/他Sourceは一切呼ばず、原3/24再演なし。metadata reader以外の元Test/外部/VM/DB/鍵/実原本へ接続しない。正式/工数/QA051final/451/HOLD不変更。

生成memberの適用性：当recordのraw classfileは明示constructor/anyReference/toString三と、compiler生成hashCode/equals/四getter六の計九methodを持つ。固定JaCoCo0.8.15の既公式generated filterを変更せず使用し、PTのapplicable METHOD分母は手書き三。四getterは001で全15許可tupleを実assertし、hashCode/equalsは独自業務logicのない固定JDK25 record生成実装としてtoolchain範囲へ区別する。手書き三/全14branchを除外しないこと、全一classを測ること、追加exclusion設定0を独立確認する。raw九methodを全て手書き三のcoverageで実行証明したとは報告せず、通常のrecord filterをcoverageだけのために変更/追加しない。
