# Named DTO全69型の独立方向別field仕様

2026-10-15、BUG1288/YKT1054、関連BUG1285/YKT1051。Production a9/PG2802不変更。
P001-03/T02/T04及びP002-P04/P05の個別oracleを補強する。旧往復試験は補助propertyとして残し、それだけで295項目の意味対応を認定しない。

## 発見・独立反例

PG3294-before-v1はserver JDK path誤認によりcompiler生成前1（BUG1286）、v2はStandalone launcher依存漏れにより最初のcompile6error/1（BUG1287）、両方ともJUnit未実行で合格加算0。修正62947c078/285b40e21の元java.home・tools/JDK25.0.4・実engine同version launcher資格/純四を経て、before-v3/exec28441は08:54:49.720264～08:54:56.241874Z actual0。正常二selector成功を維持したまま、LoginRequestDataのUsername/Passwordをfrom/fields両側で相互swapしたshadowが実一JUnit成功、安定誤byteを返すshadowも実並行一JUnit成功、見逃し二を実証した。payload SHAa476e3435e6b854fdb28052c07444ef48d05bca51528f4cd9ae8cdf4067f7e22。全原source/Jar/libとprivate raw/失敗は保持、Main/VM/agent/coverage/PT加点0。

## PT-PRO-DIR3298-001

対象=PayloadTypeCatalogTest.allNamedTypesHaveIndependentDirectionalFieldMeaning／Test-only IndependentNamedFieldOracle。実class lookupはactualであり、expectedは独立SS323全64型名fixture及びUI234～236 field fixtureから作る。PG3284が正本との64/389/74領域/69型対応を直接照合済み。

入力/期待値：

- 手書き`named-accessors-independent.tsv`の135 wire名→public accessor名を明示レビュー。値はこの対応表・UI型/必須/byte長とSS323 Java型規則から独立に設定する。Production mapper/generatorから期待値やfield順を抽出しない。
- 全69型の非固定295component、任意X/C/O79component、空request4型を独立fixtureから数えたliteralと照合。再利用型の複数layoutは同じ独立field shapeを要求する。
- 同型の複数string/ID/日時にordinalの異なる値を与える。日時は固定Instant `2026-09-02T03:34:56Z`＋ordinal msと標準Java日時/JST算出、UUID/hex/ULID形式は固定書式、数値は独立ordinal、enumはUIの明示name/wire二表を使う。実password/session/keyは使用しない合成fixture。
- `from(independent FieldValueSet)`のactualについて全public accessorを明示名で取得し、expected型・Optional generic型と独立scalarを確認する。Productのencode結果をexpectedにしない。
- 別方向は独立UI field順と明示type規則で指定したpublic constructor signatureへ、独立scalarから作った入力だけを渡し、`fields()` actualの全keyと各FieldValueを独立mapへ照合する。入力wrapperの生成にpublic factoryを使う場合でも、その出力をexpectedへ用いない。
- 各参照constructor引数を一件ずつnullにし、即時requireNonNullと明示field名を確認。全型のfrom(null)もJava内部preconditionとして拒否、NPEを業務正常結果へcatchしない。各79任意fieldを一件ずつUnset／Optional.emptyとして両方向で確認。空4型はempty正常/null/余剰field拒否。
- `toString`は各型名＋REDACTEDのみ。public reflectionは明示APIの呼出しに限り、private reflection、getRecordComponents/getDeclaredFields/実field順推測は使用0。型/期待値をactual return valueから決めない。

本試験はDTO/mapper component契約であり、全任意項目を同時に埋めた入力が業務semantic validatorも通ると主張しない。業務相関は既PayloadSemanticValidatorTest全八methodへ残す。全consumerの業務受入、全PGPT完了は本caseの範囲外。

## PT-PRO-DIR3298-002（P09是正）

PayloadGoldenVectorTest.sharedCodecProducesIdenticalBytesUnderConcurrentUseのactualは8worker/barrier/全futureのまま維持。expectedはUI234 LGNREQ01の384byteを全space初期化し、0開始offset0/64/320にliteral Aを設定する（Username1/64、Password65/256、Client address321/45、Reserved366/19）。Production codec呼出しでexpectedを生成0。PG3292はこのminimumを含む全287hashを正本から独立計算してfixture一致を確認済み。新Test数は増やさず、既一methodのoracleのみ是正する。

## 実行・受入

固定clean後`pg3294_protocol_directional_oracle.py after`：正常二成功、同じ二shadowが各実JUnit AssertionFailedErrorで拒否されること。診断四caseをProduction PT/coverage数へ算入0。

関連Protocol群は新一methodを含む85PT/17suite/174Main、四counter100/静的0/FES-flaky-notrun0、全member a9同byteを要求する。その後、必要一全回帰3702PT/542suite/1643Main（新suiteなし）、独立全XML/static/全Main/同native28 byte・CRC/session資格を一群で実施する。旧全3701の結果を新Test集合へ流用せず、Main/Jar/署名/配備/Root/VMの再実行は不要。

実source/run/command/環境/終了code/時刻/coverage/証跡hashは後続結果へ保存する。全対象・実反例・関連/全体/同byte資格が揃うまでBUG1285/1288及びYKT1051/1054を未完、P001-03/P002-02の受入も未認定とする。群開始見積りはevent0848（DTO .5/1.5/3.5pp、P09は0847範囲、全体はK01へ別記）。共有消費を実費へ推測配賦せず、N/Tnullを保持。
