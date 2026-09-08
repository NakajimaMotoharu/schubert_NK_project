# SSC-031 管理認証preludeの探索・範囲

SSC起票bc26368、SS/PT先行補足36d21f1、PG-D-082の責務確定660b3be。UserCommandは未接続のためSSC-031は対応中を維持する。

| Run | 実行日時（JST）・結果 |
|---|---|
| PT-ADM-auth-explore-01 | 2026-09-08 15:08:07、全操作kindの実User/advisory/session lockとnull/write契約2件PASS |
| PT-ADM-auth-explore-02 | 15:11:03、追加testのResultCode import不足でtestCompile不成立。fixture側のimportを補足しProductionは変更せず、合格に算入しない |
| PT-ADM-auth-explore-03 | 15:11:55、PT-ADM-008～013の6件全PASS。新規AdminCommandAuthenticator/Mutationのline/method/class/branch100%。正式全gateとは区別する |

実User rowを別ConnectionのFOR UPDATE NOWAITで検査し、必要集合だけ取得していることを確認。advisoryはpg_locksで固定key71419601/同backend/減員操作のみを確認。非locking候補lookup→必要advisory→User ID昇順→session owner lock→通常verify/touchのSQL順を確認した。候補は許可ではなく、途中のowner/role/expiry/revoke/欠落は拒否する。

相互target試験は実認証を行う2 transactionをlatchで競合させ、片側rollback後の通過と、先行側の合成role変更commit後の後続403/rollbackを確認する。これはUserCommandService本体の更新・監査の完了を主張する試験ではない。100並行の認証は各独立Connection・contextで完了し、通常touchだけをcommit、対象USER sessionは不変。SQL/必須NULL/未知actor/owner範囲/順序/close併発/時刻overflowの後条件と固定例外・caller所有を確認。

生context/hash/UUID/SQL結果はGitへ保存しない。正式source commit、日時、環境、終了code、command、Test ID、coverage、sanitized JUnit、hashは正式実行後の同Program manifestに収集する。新規暗号key、外部電文、API権限、Current baselineは変更していない。
