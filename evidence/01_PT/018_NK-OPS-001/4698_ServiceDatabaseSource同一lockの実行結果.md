# ServiceDatabaseSource 同一lockの単体実行結果

2026-11-19 JST、dev-foundation。製品Core ecf8a00fbd37720b80f8e107d59727723c706a12、Unit 73e0eae9be642e30e4a84694a4aede3f38cdc9f8。JDK25.0.4、Maven3.9.12、JUnit1.13.4、JaCoCo0.8.15。PG39866で元31とPT-OPS-DBSRCPORT-016が初回全32成功、失敗・エラー・skip・未実行0。同じ失敗本人と空Propertiesの後、別threadが次の合成JDBCを取得し、呼出側だけが一度closeした。実DB接続なし。

PG39868独立postで元31と新一のXML、CRC、単一execを確認。生のSource L75/M19/C1/B22/I284、Admission L57/M8/C1/B30/I202は全到達。支援クラスの生未達は保持。公開ABI、元接続本体・認可検査・秘匿・消去順は一致。PG39862は全四moduleの482 Main・1102物理、PG39864はBootstrap201のSpotBugs全0。最初のテスト静的指摘1を保全し、Test定数修正後PG39865の適用・未分類0。製品再build・全PTの再演なし。

実行環境、コマンド、入力、XML、exec、生counter、hashは [PG39868 manifest](evidence/PG39868-p00405-service-db-state-lock-independent-v1/manifest.json)。SHA256 5aa80f04cdef294762b856adb9acd95b1079f7105d90f0042ec6ee499b476c5d。BUG-3312/3313は当範囲完了。P004-05実接続と全451は未受入。
