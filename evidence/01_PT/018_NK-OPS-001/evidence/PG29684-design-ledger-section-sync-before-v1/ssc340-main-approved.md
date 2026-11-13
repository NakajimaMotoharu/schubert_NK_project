## SSC-340 nullable複合CHECKの三値論理と条件付きNNの内部具体化（2026-11-13、PG、設計記述確定）

状態：設計補足確定（remote公開の成否は三fileのGit履歴と照合記録を正とする）、DDL/製品PT未完。関連BUG2846/YKT2405、WBS-P004-01.01～03。既承認SS331§4.2/5/6.4/7.1の条件付きNN、snapshot pair、参照type別排他を、CHECKのNULL/UNKNOWN通過で失わせないことを明文化した。auth_sessionsも既revoked/time/reason条件を、未失効は両NULL・失効済はtimestampと既6値reasonの両NNとして具体化した。RD/UI/外部wire・列/状態/暗号profileの変更はなく、SS内で合理的に確定できるため新QA/RDF/UICは不要。

確定内容：SS331 SSC340に五constraintのTRUE必須/許容NULL・V001～028及びrolesの不変/append-only V029・不整合legacyを推測補修せずrollbackする条件を記載。SS354 SSC340にPT-DB-NULL340-001～015の独立正常/NULL/境界/拒否/対象constraint名/upgrade rollback/hash/schema・権限後条件を具体化。role/grant/table/column/index/保持・既成功値を変更しない。Source資源・版/BOM/影響Test/traceと実DB再試験は後続PG/PTで未完のまま追跡する。

main公開はorigin/main起点の隔離sparse worktreeでSS331/354/914の三mdだけを通常commit/pushし、未受入code/config/tool/evidenceを含めない。適用commitは三fileのGit履歴とremote照合記録を正とする。実DB/SQL/migration/権限・VM・原本/鍵/nativeHOLDは維持し、静的代替をDB PT/PASS/coverage/正式1964PT/53scope/全PGPT完了へ加算しない。[PostgreSQL18公式CHECK仕様](https://www.postgresql.org/docs/18/ddl-constraints.html#DDL-CONSTRAINTS-CHECK-CONSTRAINTS)もNULL semanticsの独立根拠とした。


