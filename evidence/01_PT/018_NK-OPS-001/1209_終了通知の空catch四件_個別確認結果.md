# 1209 終了通知の空catch四件：個別確認結果

Program NK-OPS-001/NK-WEB-002、SS342/343/352、PG-D334/369/378、F03。source2bbb85a29・元3939を保持する。通常PGのsource点検であり拒否PT代替ではない。

`pg5798_lifetime_empty_review.py`実0、生成negative unit1/pyflakes0。PG5770型factsの対象owner全sourceと全実class byteが当3939と同一である範囲だけ再認証し、次の四座標を個別確認した。一般的empty catchや別ownerへ拡張しない。

| source/line | 独立確認事項 |
|---|---|
| ApiProcessLifetime.java:120 | removeShutdownHookの既shutdown拒否だけ。finallyのfinished通知を失わせず、callerの資源確認を代替しない |
| WebProcessLifetime.java:88 | private state lock内のstop/installed更新後、同hook除去拒否でもfinally通知。外部process終了の証明ではない |
| WebProcessLifetime.java:107 | InterruptedExceptionは有限観測tickのwakeだけ。retainUnknownの外側保持loopを抜けず、cleanup/成功化しない。割込再設定によるbusy loopを作らない |
| ServiceProcessResources.java:195 | release/ownedReleaseの失敗frame内で観測を続けるtick。再release/下流unwindをせず、pending資源を確認済みにしない |

型facts・空body・禁止transfer/代入0・完全owner source/byte・周辺finally/外loopを照合。元3939のApiProcessLifetimeTest/WebProcessLifetimeTest/WebUnknownRetentionTest/ServiceNativeReleaseTest/ServiceOwnedReleaseTestのactual XML identityを対応付けた。元PTを再実行せず、新PT/native/coverage/正式/実VM確認の増分0。観測コードの静的根拠は、現在のVMや資源が本当に保持/終了している証明ではない。

公開`evidence/provisional/PG5798-lifetime-empty4-v1/manifest.json` SHA256 `dd2928921bae7193dcd95e1a604a85393abb3d8554a944247ebb8b6dd4e22c5c`、decisions `fb09aa6f14105d6018423350304391a6eafb4d8f592dd579ec1e6469a0f880cd`。raw1585を保持、新個別根拠4→累計480、CONTEXT261/REQUIRED215/FP4/未review1105。F03全体/global100/451/正式は未受入、工数率null。
