# NK-DAT-001 Storageの並行試験診断

SS333・341・343、WBS-P003-08/2、BUG-3916、YKT-2997。ResourceScopeとFactoryのJDK合成試験だけを対象とする。

| Test ID・既存method | 独立期待と境界 |
| --- | --- |
| ResourceScopeTest#concurrentScopes | 64 taskの独立整数 i+42 と解放総数64。各Futureと終了の上限10秒。 |
| FactoryResourceScopeTest#factory012NestedAndParallelScopesKeepIndependentOwnership | 外・内の固定6操作順、二ownerの結果と解放を独立確認。 |
| FactoryResourceScopeTest#factory018ParallelCompleteOwnersNeverShareTransferState | 二ownerの同一性と互いの非共有、open2、close0、元のLatchと10秒。 |
| PT-DAT-STORAGE-WORKER001 | 一次例外と停止timeoutを代理で発生させる。一次の実体、従属停止1件、単独時の停止例外、停止→待機10秒の順を検証。 |
| PT-DAT-STORAGE-WORKER002 | 停止待機に既知の割込みを投入し、元causeの同一性、呼出順、割込み旗の再設定を確認。 |

PG45700のmanifestに、正規Storage、元の入力と対象、選択実行、静的結果、生coverageを記録する。実ファイルとnativeを要する既保留試験は別の範囲とする。
