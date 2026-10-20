# 1297 API JMS close所有：S2独立PT仕様

NK-MSG-001/NK-OPS-001、主WBS-P018-05/P005-03/F03参照追加費0、SS321342354/SSC314/BUG1548/YKT1307/PG-D463。群1490の1/4/10ppを維持、S2内数.5/2/5pp非加算。PGを省略せず、状態/排他/成功phaseを修正する。API外部処理/電文/ACKrollback/credential/権限/SQL/親期限は不変更。

PT着手前判定 **PT_DEFAULT**：host固定JDK/Maven、自己所有dynamic JMS proxy/有限CountDownLatch/Threadのみ。外部broker/network/VM/DB/Root/cohort/intent/permitへアクセス0、拒否境界探索0。全API既存Testを後続で選択する場合は既許可のin-process/専用fixtureだけで、追加拒否操作の再試行にしない。既成功確認の再演ではなく五Main変更の必要影響試験。原本/鍵/Current/stash不操作。

001=三consumer各Runtime/Error first-close故障、false-ready・同一Error/通常fixed wrapper、二回目は未知子だけcall2/他子call1、三回目全call不変。002=全三consumer同owner並行close、第一closeを有限latchで保持し第二closeが重複provider closeをしないことを確認、解放/join後call1。003=close失敗後callbackを独立stored MessageListenerから呼んでもprocessor/ACK/rollbackを発行しない。004=親三groupの逆順と成功子cache、child別故障/同一Error/全成功後冪等。005=broker三factoryの未知子/正常子cache、故障後escaped supplierはpassword取得前拒否、既固定秘匿。006=親の並行close/既startup/fatal複合の優先・null/部分群を既Testとjoin。入力内loopはJUnit件数へ水増ししない。

独立期待値はSS321SSC314のliteral phase/child別回数/順序/同一exceptionと実Thread終端。production methodでexpectedを作らない。全新fixtureはfinallyで全gate解放・own Thread join、join/assert失敗でもcleanupを飛ばさない。旧oracleの失敗後正常no-opはBUG1548として根拠と差分を保存し、実装都合の無根拠expected変更をしない。

実行command/source/時間/OS/JDK/終了code/XML/期待実際/実counter/BUG/証跡path/hashは新only元run manifestと結果へ追記する。新source全API/関連Web・guard、六format型nullSpotBugs、原XML/六Jar/全Main物理/当target四100を要し、coverage未達は未達。全体/当static理由/traceは関連S3と群でまとめる。S2はnative返却前UNKNOWN保持・外側借用依存/当native/CHR/451の完了を意味しない。正式1964-53/17-190/工数null/QA051final/PTALT未特定は維持。
