# 閉Web認証projection値境界 独立単体テスト仕様

PG17950/event3700、source6b53efeec87f3ec36a840dd8e7759656cb4aee5c未配備、HEAD61e8258e6a32aecbc2c3d98fb0cc96ecfcfcb281/dev-foundation、主F03/関連P01502追加費0、固定1.5/4/8pp cap10/fresh81-19/reset1793774153。先行3001～4/2701～2/2997後続索引を照合、旧partial全14L2M1C/11covered7missedBを保持。

NK-WEB001/FUN001/AUT001～004/UI226、origin/main8b91944d SS314§7.2.6/SSC044/PG-D103・新PG-D1112。全Main41行＋SessionPrincipal/AuthenticationContext/UserRole、SessionStoreException全bodyと通常catalog ctorだけのcalleeを確認。新quality六はSSの閉標準token型/認証flag/principal/credentials/details/authority一個という値projectionから独立設計。旧保留SessionSecurityContext等のwholeからmethod/fixture抽出や代替実行0。3002で留保した条件を正規新Test/source固定で検証し、旧成功の再演/転用0。

|Test ID|入力・操作|独立期待値|
|---|---|---|
|CLOSED-PROJECTION001|null、公開fixed keyラベルのanonymous DTO|Optional.empty、実session削除や匿名権限認定ではない|
|CLOSED-PROJECTION002|公開Display_User/a×64/fixedInstantのUSERとADMIN snapshot、内部projection factory|標準exact token、同principal identity、credentials/details null、ROLE_USER/ROLE_ADMIN各一個、再読で同principal。null principal factoryはAPI違反NPE|
|CLOSED-PROJECTION003|foreign Testing token・標準のsubclass・未認証標準token・foreign/null principal|固定SessionStoreException、message=session storage is unavailable/cause null/suppressed0|
|CLOSED-PROJECTION004|標準認証DTOだが公開合成credentialsまたはdetails有り|同固定拒否、値を黙って消して受入しない|
|CLOSED-PROJECTION005|authority無し/二個/逆role/unknown role/null authority文字列|同固定拒否、一個の正しいrole以外をgrantしない。元入力authorityを変更しない|
|CLOSED-PROJECTION006|正規DTOを読取→details付与→除去→未認証flagへ変更|各回の現値を再検証、受入/拒否/受入/拒否。前回受入をcacheして不正を通さない|

Springのtokenは自己JVM内の合成DTOのみでSecurityContextHolder/SessionRepository/Filter/login/APIへ一切設置しない。実認証/権限付与/session発行/CSRF/operation token/credential/key/DBJMS/HTTP/VM/Root/native0。Anonymousの公開keyラベルはString hash用非秘密値で暗号keyではない。SSEはctorだけでpreserveFatal/Throwable graph走査0。固定メッセージとshallow getCause/getSuppressed lengthの確認はgraph分類ではない。Thread/executor/乱数/UUID生成/時計/IO0。並行/実再送/取得期限は当不変stateless projector責務外。

独立expectedは上記手書きclass名/ROLE文字列/固定例外・null/boolean・入力identityだけ、Production戻り値でexpected生成0。全一Source一Codeの14L2M1C18B（既同分母）を新六一JVM/単一execでCRC/全physical閉包・通常Jar/snapshot/現source固定して測定。旧partialは履歴保存後に置換/execunion0。Test subclassの追加physicalも独立CRC確認し、Main分母へ誤加算しない。公式filter不変更/安易な除外0/Failed flaky skipped not-run非合格。

command python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/pg17950_closed_web_projection_six_pt.py。normal14216/Spot14224はMain不変更で再用。XML・actual環境OS/JDK・時刻/終了・branch/HEAD・input/Test/class/exec hash/counterと独立結果は3445/manifestへ。新quality六は普通5786へ混ぜず別集計。正式1964/53・歴史17/190・新WBS受入0/工数null/QA051final/451/全HOLD維持。
