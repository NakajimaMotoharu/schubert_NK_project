# F02ファイルログhandlerの単体仕様

NK-OPS-001、WBS-F02-a、SYS-005、SS311 §3／§5.2・SSC028。対象はModuleDependencyAuditのコンストラクタ呼出分類。Process、file、loggerを起動しない。JDK 25の`FileHandler`は既定・名前付き・rollingの生成時にファイルを開く。`StreamHandler`と`MemoryHandler`は与えた引数自身を扱うfixtureとし、所有範囲・直接ファイルだけを評価する。

| Test ID | コンパイルのみのfixture | 独立判定 |
|---|---|---|
| PT-F02-LOGFILE001／002 | Web ControllerがJDK FileHandlerを既定・名前付きで生成 | CONTROLLER_BOUNDARY各1 |
| PT-F02-LOGFILE003／004 | ProtocolがJDK FileHandlerを既定・rollingで生成 | FRAMEWORK_FENCES各1 |
| PT-F02-LOGFILE005／006 | Controllerの出力stream・Protocolの合成logger用MemoryHandler | 該当違反各0 |
| PT-F02-LOGFILE007／008 | 非Controller Web adapterとBatchでFileHandlerを生成 | 該当違反各0 |

ソースに対する既知ルールの期待値を先に固定する。同一修正版で既Controllerファイル、Protocol Path、Archiveの三群35件を影響範囲として照合する。比較物は診断キー／元type／対象typeを完全一致。JDKのコンストラクタ記述と旧生証拠を独立参照する。実productについては当scopeの該当箇所とsourceを照合し、全六製品Jarの代用はしない。
