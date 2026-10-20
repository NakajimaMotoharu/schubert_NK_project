# 1245 接続readiness二owner：28静的契約点検

WBS-F03/群READINESS_FATAL_RESOURCE_BOUNDARIES、開始見積0.25/0.75/2共有pp固定。Production288062f39/851-1666のApiDependencyReadiness.verify/probe、WebDependencyReadiness.verifyを、既SS311/321/342/352・PG221/234/266/BUG248249250321と独立既存PTへ横断点検。API PT-JMS019/022/023/025、Web PT-SCR113～116/136137。実providerやRootの現在所有は点検対象でなく、未特定拒否PTの代替でもない。

DB/JMSのfactoryから受けたprobe scopeを必ず一回closeし、検査失敗をprimaryへ保持。通常SQL/Runtimeは値/cause/suppressedを外へ出さない固定startup例外へ変換し、致命Errorはidentityを保持する。closeが失敗した場合の独立契約表は次のとおり。これはレビュー表であり新たに動的試験した件数ではない。

| 検査primary / close | 成功 | 通常失敗 | 致命Error |
|---|---|---|---|
| なし | 正常 | close通常失敗→固定診断 | close Error同identity |
| 通常失敗 | primary→固定診断 | primary→固定診断 | close Error同identity |
| 致命Error | primary同identity | primary同identity | primary同identity |

反証点検：TWRだけへ機械変更すると通常primaryが致命closeを隠し得る、無条件finally throwなら既fatal primaryを上書き、Errorを外側Runtime redactionへ加えれば致命failureを通常化する。現PGは全4箇所で条件付きfatal優先を保ち、secret/例外graph traversal・retry・成功補完なし。既API六compound testはassertSame/固定診断/cause-null/close1/DB失敗時broker0、Web scr136137は同三組合せとclose/取得回数を独立proxy/literalで検査する。他正常/null/取得失敗/実隔離PG/in-process brokerの既fixtureもTest source/semantic identityで対応させた。新sourceの当Test実行結果はまだ元whole終端待ちで旧成功を輸入しない。

5960独立guard fixture1/pyflakes0・実レビュー0、generic20/条件型判定4/finally4を個別span/source/current型fact/関連Testへ登録。公開`evidence/provisional/PG5960-readiness-boundaries28-v1/manifest.json` **b24e154dde5b57f62f4a87081ea34ee001c89eb9e9b5226d63caa034a87912f3**、decisions **4a1fa2f1564ee92878567c9d9251bee66746431752c9dad63ed57fb6d1db9758**。PGの確認結果=この二ownerの当契約に変更不要。新28理由により**新whole待ち573/未点検878/raw1451**、raw抑制/除外/削除0・実PT追加0/代替確認0。blocking上限/真正Root/DONE/現在接続・DB不変/lock解放/native/CHR/正式品質は後続依存で、この静的点検を実証へ使わない。
