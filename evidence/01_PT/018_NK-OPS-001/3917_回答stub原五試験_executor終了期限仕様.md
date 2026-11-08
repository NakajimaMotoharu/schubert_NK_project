# 回答stub原5試験のexecutor終了期限

G03.05主/P01202関連追加0、REWORK原1/4/8pp cap10。対象は既存StubAnswerProviderTest全5method/PT-ASY-STB001～005とMain StubAnswerProvider/AnswerResult、AnswerProvider宣言。元2925/2926・3867のpublic clock/空回答/64時刻/identity/null/赤字化期待を保持し新Test設計/部分抽出0。Main source7aed不変更。

BUG2559/YKT2177へ修正前登録。timed invokeAll5秒は保持し、返却後Futureは完了/取消済みでありget()を新しい無期限wait障害と断定しない。TWR executor.closeだけが失敗時の無期限回収となるため明示finally shutdownNow→awaitTermination10秒assertへ変更。timeout/cancelled/終了未達を失敗扱いにし期待値を変更しない。

元Test SHA256 `ac4d482aeaa66f017973eddcff1858990a7ef4d3f07ca03138c1a1ebf6f2dceb`、beforeはGit object/現byte hashのみ（Source本文のevidence複製なし）。MainとTest/helper/全initializerを読取済み。時計はmemory supplier、IOは新専用cwdのtarget/question-stub-tracesに固定公開文字列を一件書くTest専用操作のみ。実DB/JMS/HTTP/auth/session/token/鍵/Graph/Root/native/VM/権限変更0。held4のcompile/init0、protected二Test/二工具にはIO0。

format→testのみjavac release25 -Xlint:all -Werror→許可されたTest静的確認→source固定push→元whole5を一回実行/外側180秒→独立XML全5/FESflakyabortednotrun0/期待output/同session同CRC/counter/held4未初期化を検証。必要Sourceのcounterは実測値を保持、自然B0はN-A/nullで四100と偽らない。環境・SDK/JDK/normalMain22084/22086・全実行command/exit/path/hashをmanifestへ保存。新unique/Source登録/leaf0・正式1964/53工数null全HOLD保持、全YKT2177閉鎖0。
