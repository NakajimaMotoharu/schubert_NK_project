# 2627 UserCreateForm 元whole八件 単体テスト仕様書

2026-10-30 JST / branch dev-foundation / source6b53efeec87f3ec36a840dd8e7759656cb4aee5c / PG-D878。群3014 開始0.5/3/5pp cap10、最初の候補読取からevent記録までの遅延をeventに明記。Main全161行・Test全324行、UserCreateRequestData全body・UserRole全body・TypedFieldValues追加enumValue/flagを確認。共通codecの既読実経路を使用、expected側は372byte配列の手書offset/ASCIIspace/JDKのみ。先行2058は旧レビュー参照で新source合格には転用しない。

Program=UserCreateForm/bind/invalidCharacter/displayValues/getIssues/toRequest/close/toString、Main canonical P016-16、元TestはUNKNOWN/null。関連SCR016/FUN009/AUT002/UI225,236/SS313,314,323(UCRREQ01)。元testの8 method全体だけ、1suite/newTestIds0。PT-USER-CREATE001..008＝create001..008。

|ID|入力/操作/期待・独立根拠|
|---|---|
|001|USER/ADMIN×enabled真偽、username/password/role/flag/UUIDを372byte手書goldenとactual codec比較。offset0/64/320/325/326、全spacepadding。認証権限発行はしない|
|002|username1/64byte、password12/128codepoint・256byte、NFC結合文字・emoji・先頭spaceをliteralで確認、passwordをtrimしない|
|003|欠落/0又は複数値/未知field/CSRF参照非保持、map/key/list/要素nullの明示例外、ProductionでNPE catch正常化なし|
|004|username65/不正ASCII・Unicode、password11/129codepoint・257byte/controls/surrogates/trailing space/username同一を拒否|
|005|確認不一致、role/flag未知、UUID大文字・長さ・未知文字を拒否、authorityやsessionの試験ではない|
|006|元map/list変更後にsnapshot不変、redisplayから合成secret/token除外、issues immutable、close二回後toRequest失敗|
|007|自己所有8thread/100有限task・get10秒、各独立literal/golden、実network/DB/MQ/file/application操作なし|
|008|invalid確認文言のliteral、redisplay/例外/close後条件、無効な入力から送信できない|

判定PT_DEFAULT。全Test helper/initializer/callback、Main/DTOとencode必要依存が純粋値処理であることを確認。実USER作成/権限変更/パスワード保存・DB/VM/Root/鍵/permit・held graph9は実行しない。入力は既存Testの合成値だけでログに保存しない。並行は自己所有executorの閉鎖をtry-with-resourcesで確認。再送/業務transaction/HTTPは対象外で成功へ換算しない。

command予定 `python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg14288_web_user_create_whole_eight_pt.py`、同source14216六Jar/固定Reporterで新-only一JVM、F/E/S/重複case/timeout/実exit確認。全Source closureと一exec CRC・四counterを独立14290で測定し、未網羅ならそのまま未達。Branchは当仕様の明示値、OS/JDKは元JVMの四prefixをstageへ構造化記録（BUG2096の再発防止）。元source6b53以外や旧0061の結果/execを移植しない。独立結果・hash・時刻/SDK/command・coverage・未確定事項は2628とmanifestへ記録、正式1964/53・個別17/190・工数null・QA051final/全HOLD維持。
