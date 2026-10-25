# G13.07・型構文参照なし55件の静的compile/bytecode参照確認

2026-10-25 12:59 JST、G13_STATIC_COMPANION55_BYTECODE_V1/WBS-G13.07。開始 low1/base3/high6pp・群cap10。fresh64残36/reset1793382075、停止はfresh現在窓残10%以下/取得不能。元予実/各群開始値は比較履歴であり累計停止/抑制/小capには使わない。Production64446、原正常9246、現在所有9348の569/Java1394登録と旧原runを保全。

対象は9344 source-statusesのNO_TYPED_TARGET_REFERENCE55pathだけ。静的method/field/class literal/handle参照を、同sourceの新規専用Test静的compile出力から実行せず読み、対応Mainの既canonical責任へ結ぶ。定数inliningなどで証明できないものを推測登録しない。前群337parse/280候補は再実行せず参照する。

区分=許可されたhost静的compile/bytecode解析、製品PT実行ではない。JDK25 javac -proc:none/-implicit:noneで当55のソースだけを新規専用出力へcompileする。元normalの六Main Jar/source/dependenciesをhash固定し、必要な既test fixture class metadataを依存入力として明示する。compiler Pluginサービスがあれば未確認のまま実行せずHOLD。annotation processor/JVM agent/アプリMain/JUnit/Testメソッド/VM/Root/DB/JMS/credential入力は起動・実行しない。compilerによる型・class metadata読取と、対象のruntime class load/初期化/実行を区別し、後者は0。全体normal成功やPTを確認目的で反復するのではなく、新しい参照証拠を得るための限定静的解析である。

ASM9.10.1は新出力のclass bytesを読むだけでClass.forName等を使わない。SourceFile/packageとTest sourceを対応し、Main又は同Main内部classへのmethod/field/type/実class literal/handleだけを採る。単なるString値・descriptor類似・他namespaceを根拠にしない。独立javapの構造tag/参照ownerと突合し、raw disassembly/fixture値は公開保存しない。Main/sourceがshadowされる出力や不明な依存/provenanceは候補にせずHOLDする。

手書きの仮想class bytesをASMで構築し（ロード/実行しない）、参照あり/なし・String同名・他namespace・同名prefix・nested owner・SourceFile不一致等をliteral期待値で検証する。新規工具の初期TDD/依存構築失敗は製品PTとは区別し、実装済み工具の誤判定は915/916先行で是正する。新exact候補/未確定理由を記録し旧569/元941/943/予算/acceptanceを維持、485更新時は486参照再束縛と全WBS監査HOLDの真正結果を保存する。工具検証/静的compileを製品PT PASS/実測coverage/正式受入へ加点しない。終了後も許可済み独立PG/PTを継続する。
