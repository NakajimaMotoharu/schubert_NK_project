# NK-OPS-001 PT-OPS-MQ-022 oracle強化 PG/静的結果

3507/644645に従いBUG2242/YKT1988の一helperを製造是正した。元入力はc489ce0607cffe3e1c91b64465e20f08e3acc35864b8c3a37546bd6ecfc9923d、変更前HEAD2ff413226、Production Main6b53は不変更。更新source byte/class・compile/static/SDK lineage/独立reviewはPG18570 manifestと646へ固定する。Git source commitは次公開で確定し、旧current資格を移さない。

query/probe/brokerProbeは未知例外を伝播し、null replyや欠落/未知の失敗statusを固定AssertionErrorへ変更。falseはowned fixture user・permission・targetが一致する固定SDKの明示permission denialだけに限定。session.startはdenial catchの前、requestor cleanupは外で、close失敗もfalseへ隠さない。ClientSessionと同じpublic fixture userを非秘密wrapperへ束縛し、wrapper診断はredacted固定。passwordは保持しない。既十一操作とreply address残存後条件のTest本文は全byte同一（SHA0c0524bf6de6d2e6c1a09079a23927e7c3a046936741dfd305169b6d8eddbc0d）、既role/権限設定/selector/電文は不変更。

|確認|真正結果|限界|
|---|---|---|
|固定SDK2.56.0|公式source三artifactと既binaryのpublisher checksum照合、645に7entry/hash/行範囲|source/byte契約確認のみ、SDK brokerを動かしていない|
|横展開|884公開Test source、held二名除外、ManagementHelper同形一producer|alias/別APIの全認可監査ではない|
|compile|PG18570/74687/d73b4b actual0、-proc:none/-implicit:none/-Xlint:all/-Werror、明示一source、生成3class|Test/SDK/Fixture class初期化なし。classpathはnormal14216の外部dependencyのみ|
|Checkstyle|90284/4703f4内child actual0、指摘0|当一sourceのみ|
|PMD|child exit4、指摘6、processing error0|0/合格へ変換しない。既存literal oracle3/既fixture cleanup2はOPEN、借用client1は外側ownercloseという非該当根拠|
|独立PG review|646/d2fc44、22観点STATIC_REVIEW_ONLY_NOT_EXECUTED|無応答/通信/unknown/NPE/authentication/別user・address・permission・code/malformed UUID/cleanup等。動的入力による実行結果ではない|

実command/source/dependency/class hash/開始終了/exitは公開manifestに収録。原SDK source jar/raw工具stdout/未加工XMLはown PG379 host slotへ保持、Gitはmetadata/source hashだけを保存。公開SDKリンク/byte lineageは645、既原失敗/old PT/Current baseline不変。新しい経路/モック/fixtureで実broker拒否PTを代替実行していない。

実PTはNOT_EXECUTED/HOLD_SCOPE_UNRESOLVED、実測coverage=null、PT実行免除なし、実RBAC/資源後条件/全451/trace/個別受入を未完のまま保持。PGは省略せず必要是正と許可済staticを行ったが、未実施PTのPASSやcoverage100へ混ぜない。BUG2242/YKT1988はPG_STATIC_PARTIAL・dynamic/fullquality待ちでOPEN。更新コードでの真正broker応答・transport/missing/wrong-denial/cleanup負例・same-source全品質が次の終了依存で、既HOLDを自動解除しない。

本通常群の元見積0.3/1/3pp・cap10は不変、S/V予算と別記録。S7/10/初回V未達/PLAN_NOT_VALIDATEDを変更せず、新V/新S/モデル/agent/chat/券課金0。正式1964/53・工数null・新Product試験/個別受入0を維持する。
