# G13.07・未登録Test sourceの直接companion静的AST抽出

2026-10-25 12:24 JST、G13_DIRECT_COMPANION_STATIC_AST_V1/WBS-G13.07。開始 low1/base3/high7週次共有pp・群cap10固定。fresh63残37/reset1793382075、停止は477/1899のfresh現在窓残10%以下/取得不能。累計予算停止・大型群抑制・小capは適用しない。source64446/正常9246と現在の原9334所有289/全Java1789/登録1114/未登録675を保全する。

未登録675pathを上限母集団とし、同module/同packageに完全一致するMain.javaが存在するFooTest.javaだけを候補抽出する。既正本Main owner/costと当source hashを保持し、JavaParser3.28.2によるASTで実型/constructor/class literal又は固定class scopeの参照を確認する。コメント/文字列だけの名前、同名type/変数/型変数のshadow、他packageの同名import、parse不明やpackage不一致は採用せずUNKNOWNを保持する。曖昧なTestをMain名の類似や作業群名から割当てない。

抽出は所有候補/trace不足補完であって、全method/要求/TestID/oracle受入ではない。直接対象責任と依存する共通class責任を重複費用化しない。提案catalogのsource/Test/Main hash・owner/cost・解析statusを固定し、その後の独立metadata/別経路検査で確認できた分だけ明示候補として登録する。parser出力だけで正式受入・PT実行/coverageを計上しない。

実行区分=許可されたhost静的解析工具の製造/独立fixture検証。自己所有JDK25 javac -proc:noneとJavaParserだけの新JVMでpublic Javaソースを文字列/ASTとして読む。対象Production/Testのcompile・class load・JUnit・Main/run/native/DB/鍵/VM/Root/network処理は一切行わない。parser classpathは既配置official javaparser-core3.28.2の単一jarをhash固定し、target module Jarを入れない。副作用は新規専用工具slot/公開metadata receiptのみ。HOLDや拒否対象の探索/再試行に転用しない。

手書き独立小vectorで実参照、コメント/文字列だけ、同名shadow、他import、package差、parse失敗等を確認する。未実装工具の最初のTDD失敗は製品障害と区別し、実装済み工具の誤判定は915/916を先行起票して是正する。675全体と実parse対象/成功/不明/採用候補の分母を別記し、未parseや失敗を登録済み/PASSへ転用しない。必要なsource/byte・旧289・元941/943/予算/acceptance保持、485変更時486再束縛・全WBS監査HOLDの真正記録を維持する。終了後も依存順に許可PG/PTを継続する。
