# 質問・通知query SQL前境界・単体仕様

2026-10-26、2036/ADM083と同群開始1/3/8 cap10、原QuestionQueryRepository=P01401担当費を保持。QST005～010/NTF001～012/AUT002003/UI224236241/SS312323332354/451。Main/上位仕様変更なし。

QuestionQueryPreSqlBoundaryTestの新PT-QRY-PRE001～004はquestionSearch/notificationSearch/questionDetail/notificationDetail各entryのconnection/actor/request単独null、全NPEで各名前固定/JDBC0。PRE005はUSER＋公開Username filter=other、VALIDATION_ERROR/固定question query is unavailable/causeなし/JDBC0。PRE006はADMIN＋Username65ASCIIbyte/X64、constructor保持後FieldEncodingException/JDBC0。page1/size50、IDは固定N12 8/9、Optionalは独立literal/empty、Production出力を期待へ用いない。

JDK Connection自己Proxyは一切のmethod呼出しを数えてAssertionErrorとし、SQL例外を注入しない。全fixtureは合成入力/メモリだけ、非秘密actor Role/IDを使い実認証をしない。全六methodはSource2036で確認したtry/JDBC前だけ、paged/detail SQL helperや保留preserveFatalへ入れない。保留Main二/SQL helperのprobe0を独立postで検証、違反なら合格化せず保全。Root/VM/DB/既fixture/鍵/サービス/ネットワークは不操作。

正常SQL/owner predicate/再送/並行/DB後条件の受入は別残件。本六の成功だけで全Question/Notification受入や全coverageを宣言しない。先行PG/static/format/normal後、ADM七と同一source/runの計13/3を一回実行、各methodを一意TestIDで追跡。結果/実command/env/commit/終了/XML/complete source counter/hash/BUGは008へ、全Main/他Test不変とsource/traceをshared postへ保存する。全HOLD/QA051final/正式1964-53/17-190/工数nullを維持。
