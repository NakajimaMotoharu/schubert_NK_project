## SSC-340 nullable複合CHECKの三値論理と条件付きNNの内部具体化（2026-11-13、PG、変更前起票）

状態：起票済・設計補足未反映、DDL/製品PT未完。関連BUG2846/YKT2405、WBS-P004-01.01～03、SS331§4.2/5/6.4/7.1・SS354。承認済みSS331のMUSIC pair半端状態拒否、Notification ERRORのcode/message NN、Inbox snapshot両NN又は両NULL・参照type別排他ID NNを、PostgreSQL CHECKのUNKNOWN許容で取り逃がさない具体的条件へ補足する。auth_sessionsは既revoked/time/reason整合を、未失効は両NULL・失効済はtimestampと既6値reasonの両NNと明示する。これは既列・状態・列挙値・暗号profile/外部wire/UIの変更でなく、既複合条件のNULL評価を確定するSS内部補足であり、RD/UI修正・利用者業務判断・新QAは不要。

対応予定：SS331へ五constraintのTRUE必須/許容NULLと独立負例、V001～028不変のappend-only migration V029、既存不整合は推測補修せずmigration transactionを失敗・rollbackすることを記す。role/grant/table/column/index/保持・成功値は変更しない。SS354へ5群のNULL半端/正常/境界/既データ拒否・rollback・hash/独立SQL後条件を具体化し、記述確定・整合確認後に設計only隔離branchでmainへ公開する。未受入DDL/code/Test/工具/証跡はmainへ混ぜない。

実DB/SQL/migration/権限・VM・原本操作のHOLDは維持する。public review/許可静的代替を実行済DB PT/PASS/coverageや正式1964PT/53scopeへ加算しない。後続PG群でSource/新旧checksum/対象Tests/静的証拠を一度だけ対応し、当SSCは設計公開・実装・実DB再試験の各状態を分離する。条件付きNNの根拠はorigin/main既SS331と[PostgreSQL18公式CHECK仕様](https://www.postgresql.org/docs/18/ddl-constraints.html#DDL-CONSTRAINTS-CHECK-CONSTRAINTS)であり、production式をexpected生成器にしない。


