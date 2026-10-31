# JLS25変換ゼロ限定span 工具資格仕様

2026-10-31/PG-D1022/event3492、主・計測WBS-F03、開始.5/1.5/4共有pp cap10。HEAD3fa926f52c11fec148f09fc83392ce0eefec462b/push98930終端b85bcb真正0、Production6b53/normal14216不変更。fresh20:59used59/rem41/reset1793774153/短期null/券0、実N/T・専有費・工数null。

一次根拠は[Java SE25 JLS §3.2～3.4](https://docs.oracle.com/javase/specs/jls/se25/html/jls-3.html#jls-3.3)（2026-10-31参照）。まだeligibleなUnicode escapeが現れていないという不変条件の下では、raw連続backslashの偶奇でeligibilityを判定できる。最初のeligibleなbackslash直後がuなら、多重u/不正桁も含め直ちに未解決として拒否する。したがって受理したtextでは変換済み文字が存在せず、Unicode変換による行/列変化も無い。ineligibleな二重backslash中のu表記は通常のraw文字列のまま。これは全Java lexer・escape decoderを実装する計画ではない。

新guardはSourceを修正/マスクせず、LF以外の行/EOF曖昧control、UTF8不正、null/欠落/不正座標・対象行非ASCII/tabをfail closedにする。既16291 raw UTF8 byte変換へ接続し、旧pmd_source_span_ascii/既byte_spanの契約や旧失敗証跡を変更しない。必要な文字列metadataの正常/境界/異常反例だけを固定し、別方式のregexで先頭escape判定と行prefix/byteを独立照合する。

実Product/fixture/compile/JUnit/coverage/Graph/DB/JMS/Root/VM/permit/鍵/拒否対象操作を実行しない。既公開Source三つの全byte SHA・原XML/対象座標へ適用可能性を照合するだけで、Source用途レビュー・PT免除/実行PASS/coverage/正式受入にはしない。eligibleがあれば対象だけ座標未資格を維持、通常の静的読取を動的HOLD解除へ使わない。結果/実command/終了/hash/残リスクは3177へ。
