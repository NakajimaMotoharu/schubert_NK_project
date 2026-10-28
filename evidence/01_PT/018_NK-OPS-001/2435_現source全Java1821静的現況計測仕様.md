# 2435 現source全Java1821・静的現況計測仕様

2026-10-28着手前固定。保存218157ed7ab4b400a360adace63c5e5e8eb5fd87/push93589真正0/origin一致、Production source db33c6a371d3dbc8e84f70462e0e56351bbb18b4。群F03_CURRENT_ALL_JAVA_STATIC_CATALOG1821_V1、低1/基準3/高6pp・cap10、fresh共有8/残92/reset1793774153・secondaryなし、次点検used10/残10以下又は不明で新規停止。専有費/N/Tnull、原/v3/v4/v5及び前群開始見積不変更。

## 目的・有限scope

数百件の原規約是正とBUG2043の追加観測二件に対し、追跡catalog8008と実測を混同しないためのcurrent全source静的計測を一回行う。原成功の確認再演/全PT/VM/実業務再実行ではない。1821 source＝Main965/Test856、六module、Source/設定/ツールversionを固定し全入力hashを先に永続化。旧PG10690原catalogは上書きせず、新run/source/条件/実測件数を別成果として保存する。

positive集合は固定normal13242/73d770b4のinputHashes中`src/.../java/*.java`だけ。immutable snapshot内の原source byteとworktreeを照合する。保留二工具はsrc外で対象外、内容を読取/hash/lint/compileしない。未知二Testはsource集合に含めるがfile primary/cost UNKNOWN・動的HOLDを解かず、2135/1936の完了証拠を再実行しない。

## 型・依存・独立確認

既PMD7.28.0＋record修正JAR/Checkstyle14.3.0・既rule hash/Java25.0.4を使用し除外/抑制/閾値を緩めない。auxはfresh同source六Main JARを優先し、同source compiled test-classes六rootと外部固定test依存を含める。共有ApiLogDatabaseFixture等を型解決可能にするための静的metadataであり、targetを実行/初期化せず、新harness/権限・アクセス経路の解除ではない。旧local project snapshot JAR混入を拒否する。全1843Main/1974Test class byte、1821source、全tool/外部依存hashを前後照合。

PMD/CSのcommand/exit/processing error・全raw件数を保存し、module/Main-Test/rule/path/hashで集計する。PMD0/4・CS実終了を改変しない。警告ありはqualityGate1、processing/config/parse不備・中断・未実行を分析完了/品質合格にしない。source件数とphysical class/実行Test数を区別する。独立readerはXML全件を再構成し集計/分母/hashとmeta変異反例を確認、解析自体は再実行しない。

BUG2043の二methodと原catalog各IDの見え方は観測として保存し、全体と部分の相違をコード修正済/false-positive/実障害と先に断定しない。catalog差は追加発見・条件差・解消候補に分け、単純な件数減を完了率/効果と呼ばない。source/code/業務/PT oracle/Currentbaseline/元試験証跡/原941943/481484・正式1964-53/17-190/工数null/QA051finalは不変更。結果2436/PG-D785へ保存後、必要な独立PG/PTを継続し通常群/報告/commit/PMO待ちでは停止しない。
