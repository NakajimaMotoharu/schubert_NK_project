# G13 現Mainクラス・method分母 仕様

2026-10-31 / PG-D975 / 群3385 / WBS-G13.07、開始0.5/2/5共有pp cap10固定、used50。Production6b53、normal14216の保存された六Main Jarを固定。source965/physical1843のうち、従前MainClassCodeStructureAuditV2が保持する二Graph9 classは**entryを読む/単体hashする前にHOLD**を維持する。Jar containerの固定hashとentryをparseする操作は区別する。

既存data-only JDK25 ClassFile readerをhelper-only classpathで呼び、1841のflags/SourceFile/field数/全method name-descriptor-flags-Code有無/長さを列挙する。Product classをdefine/initialize/実行せず、Compiler/旧Product試験も再実行しない。二HOLDはstructure/hash null、全1843の分母から消さず、そのmethod数は不明のまま。SourceFileから現source965へ厳密に結び、15918責任owner lineageはmethod-TestIDの証明でないと表示する。

synthetic/bridge/record/constructor等を勝手にcoverageから除外しない。NoCode分類とcoverage適用性の承認は別。method metadataの観測数を試験済み数やcoverageへ変換しない。Python独立decoderは同じ二entryを先に除外し、残1841全method/flag/Code長を別計算、source binding/欠落/重複/虚偽HOLD解除/coverage・受入昇格を検証する。原本/鍵/DB/VM/外部/私有rawなし。G13全受入/正式/工数/451/QA051final/HOLD不変更。
