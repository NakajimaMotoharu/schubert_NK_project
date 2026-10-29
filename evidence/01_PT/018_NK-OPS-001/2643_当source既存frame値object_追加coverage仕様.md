# 2643 当source既存frame実行・値オブジェクト追加coverage仕様

2026-10-30 JST、dev-foundation/Source6b53/保存4885a4f1b9fd3a86d2f9e9d60b17313d66b79acc。群3031開始0.25/1/2pp cap10、PG-D886。次のHeader/Layout新JVMより先に、既完了・同sourceの元PG14326一execが直接assertした値オブジェクト三Sourceを追加測定する。製品試験再演/新JVM test/新case/exec合成0、既133を増やさない。これは原133の新規消化ではなく当source技術測定の補完。

対象全body=FixedPayload、WireMessage、PayloadValues。完全各一physical、Main canonicalP001-03/P001-02/P001-03、NK-PRO002/UI232234/SS322§2,4,5。元2639/2640・PG14326/2f93e52f・独立PG14328/8099de1cのsource/input/親真正0/XML24/一sessionCRC・固定fixtureを参照、追加oracle入力を作らない。

一意case対応:
- FixedPayload/WireMessage: MessageCodecTest.fixedPayloadIsDefensiveAndWireMessageChecksLengths / fullMessageRoundTripsAtByteBoundariesAndRejectsInvalidSizes。固定data{1,2}/record{3,4,5}、input/返却array/list変更後に値を保持、null/negative/record長不一致/immutable・header3種類長不整合を拒否、metadata-only textual form。
- PayloadValues: PayloadCodecTest.valuesAreImmutableNullSafeAndRedacted。layout/data/records/null要素、List immutable、合成secret非表示を元assertで確認。DTO constructorをfixture入力として使うがexpectedは元literal/契約に固定、Production methodで期待byteを生成しない。
- helperのFieldValueSet.hashCode相互比較は当三Sourceの独立数値hash oracleへ使わず、当scopeに含めない。

追加tool14342はProduct classをロード/呼出しせず、既execと正常compileのexact Jar/classfile閉包をJaCoCo toolで解析する。元whole24を新24として計上せず、新postにはsame-current-run reanalysis/元case counted elsewhereを明示。四counter/自然branch0/未達は実測のまま、未実行の新機能や全fixture暗黙例外の成功へ換算しない。必要SDK/source/元環境・XML/parentpin/command/hashと結果は2644へ。Root/DB/VM/実JMS/鍵/cohort/graph9/HOLD工具二件/私有rawlog操作0、formal/工数null/QA051final/全品質HOLD不変更。
