# WebSession rollback secondary PT仕様（PG前）

BUG1592/YKT1345/1348、SS312329330/314/331/332/354。原115SQL scopeのEncryptedWebSessionRepository.transactionはrollback SQL/RTE/Errorをinline addSuppressedするため、suppression無効primaryのsecondary fatalを失い得る。既TWR Connection.close/SessionStoreのcause-suppressed-next分類と通常catalogは維持し、SQL/RTE/Error attachmentだけ既qualified WebStartup pure口へ接続する候補。権限/session/CSRF/認可/DB列/TTL/正常動作を変更しない。先行manual二ownerの原資格後に着手し、現在の固定Main/Testを変更しない。

予定PT-WEB-SESSION-ATTACH329001～003（新一class三method）：001 setAutoCommitでsuppression無効Runtime、rollbackにSQL next/cause/suppressedのError又はdirectError、同一fatal/rollback1/close1、後続readOnly/SQL/commit/session識別子発行0。002 primary graphとsecondary両fatal/直接primaryErrorとsecondaryErrorは既primary優先、同一Throwable self-attach0・close一回を保持。003 非fatalcycle/同一Throwable・欠落Connectionは原因/suppressedなし既SessionStoreException、null/異常を成功へ補完しない。期待値は固定Error identity・明示counter/固定catalog文字列から独立に作る。

PT_DEFAULT、DataSource/Connectionは自己所有pure proxy。Repository.createの返却前setupへfaultを注入し、SessionPayloadCodecは公開合成constructor入力だけ、暗号化/CSRF生成/新session ID factory/SQL/DB/VM/Root/原本/鍵/外部通信へ到達しないことを独立counter/assertで確認する。これは実Loginやsession/credential取得・既session操作の検証ではない。新Test-only原反例→一Main必要PG/全oracle固定・旧Session domain→原source/Jar/XML/counter/static→115map/まとめ必要全体へ。主担当は485で着手時に確定し、群1625開始見積/原-v4/実配賦null・正式/QA051final/全HOLDは維持する。
