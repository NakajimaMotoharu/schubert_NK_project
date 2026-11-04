# V未実行draftの静的点検・compile条件

実施ID PGPT-SV-20261104-01、V上限10pp・開始判断見積1.5/5/9ppを維持する。532は原選定として保存し、533が現在判定。製品PTはHOLD_SCOPE_UNRESOLVEDであり未起動。以下はPGの静的確認だけで、V実証成功・実測coverage・個別受入へ変換しない。

対象は `tools/quality/architecture/QuestionProjectionFailureContractTest.java` の未実行10method。具体期待値とIDは532、source hashは534。製造済みRepositoryは全body・例外/helperまで静的点検したが、製品コードを変更したという実績ではない。V対象の業務仕様・Current baseline・source6b53は不変更。

新draftは、50件・999999page/49999950recordsを手計算し、NULL/未知値/件数不整合/借用transaction/所有者/RS・PS解放/固定catalogを明示している。`projection007` のfatalは当Testが作成するError identityがexpectedであり、production graph探索でexpectedを作らない。各失敗入力を正しいrowへ個別に適用する必要があり、成功条件を満たしていないfixtureで偶然同じ例外が出ただけでは検証成立としない。現在は未実行なのでそのdynamic成立も未認定。

静的反証点検で、最初のdraftの二点（loop変数のlambda捕捉、通知検索の正常基底rowを質問用rowで代用）を初回compile前のauthoring段階で直した。534のhashはその是正後byte。TDD未実行draftを既成功又は不具合修正済みProductionとして扱わない。

許可範囲は既存normal compile manifest14216のSHAを確認し、固定六Main Jarと必要な既cached dependencyをclasspathへ置き、`javac --release 25 -proc:none -Xlint:all -Werror` でこの新Test一fileだけをcompileすること。JUnitを起動せず、annotation processorを起動せず、Productのmain/static initializer/fixtureを実行しない。Source classの実行を伴うcompile-wrapperを使わない。旧normal1962全入力のSource hashループを呼ばず、RootFailed二Test・held二工具のread/stat/hashを行わない。対象外Jarの旧内部Maven成果を外し、同normal六Jarのbyteを確認する。

command: `python3 -B tools/quality/pg18512_query_projection_draft_static.py`

新規専用slot PG18512-query-projection-draft-static-v1、begin/owner PID/command/終了code/timeout/stdout・stderr hash/compiled class hashを保存する。既存slotがあれば再実行しない。既共通stage runnerの180秒budgetを利用し、新しい同用途の実行engineは作らない。compile失敗は失敗のまま保存し、Product試験のFAIL/PASS件数へ混ぜない。静的成功でも動的HOLDは解除しない。結果・commit/hashは後続結果資料で参照する。

Vが未達でも独立S-POSTは同じS10の残枠で続ける。新しい易しい実証への差替え・追加V・新S10・モデル/agent/chat/reset/課金は行わない。
