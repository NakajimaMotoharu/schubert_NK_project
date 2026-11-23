# 合成FileStore・Heap監視の現候補試験結果

WBS-P018-09/2、SS351・354、旧仕様1582／1599。PG43486、JDK25.0.4、製品Core `87927ea17c1c8dbef528bc0c6882c24b1fe7c871`、対象試験source `8ae106e9327be5ca75f8df3f9cef1453bfebc9d0`。

| 実行 | 対象 | 結果 |
| --- | --- | --- |
| v1 | 旧合成Clock補助型が欠けるコンパイル | 終了1、JUnit未起動、BUG-3710 |
| v2 | FSINPUT008～010、HEAPCONN001～008 | 11成功、失敗・エラー・skip 0 |
| v3 | OBSCLOCK008のみ | 1成功、失敗・エラー・skip 0 |

v2はHeap観測の10行、6メソッド、1クラス全到達。FileStoreの時刻付き入口とそのラムダが未到達。既存のOBSCLOCK008は合成時計と合成FileStoreを使い、時刻付き通常経路、異常時の件数と状態不変、回復の境界を独立期待で確認する。v3はFileStore観測の10行、6メソッド、1クラス全到達。各対象クラスの命令上の分岐数は0。二つのJaCoCo実行は分離して保持。実FileStore、実管理Bean、実監視・全451は未実施。

[実行manifest](evidence/PG43486-current-two-supplied-monitors-ordinary-v2-v3/manifest.json)
