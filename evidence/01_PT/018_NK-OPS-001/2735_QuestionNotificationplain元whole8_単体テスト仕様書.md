# 2735 Question/Notification plain 元whole8 単体テスト仕様

source6b53efeec87f3ec36a840dd8e7759656cb4aee5c/dev-foundation/Gitd39ffd1015f2bb8a9971be94bb3c748d6819ef36、NK-QRY-001/NK-NTF-001/QST005～010/NTF001～012/MQ006～010/UI224/236/241/SS323/324/332、PG-D932。元QuestionQueryPlainContractTest全366行8件、Main204行、原2015spec、六typed request/response DTO・AnswerState三値/NotificationType三値/State五値/Question-Notification IDと既読Canonical/Actor/Protocol codec helperを全body確認。原2015の当初独立性を維持し、旧DB/helper/鍵寿命/Graph9/Rootの抽出や改名再演0。

全fixtureはQSS384/NTS64/明細12byteと固定actor/UUID/時刻/typed値。queryは全nullのみで非null repository/connectionを構築しない。plain CanonicalRequestの通常scope cleanupだけで、鍵/HMAC/provider/after-close/並行close/実DB/HTTP/JMS/VM/Root/業務発行/私有raw0。元Log8は既に当sourceで別群成功しているため、当群には入れず確認再演・重複費用0。

|Test ID|独立goldenと期待|
|---|---|
|QRY-PLAIN001|質問/通知optional全space、独立names5/3・X1/T1/null、owner7/原page999999/N1/size50/固定header-redaction|
|002～003|QSS offset0/256/320/332/349/366、NTS0/12/29/46、é_%/unit7/ANSWERED又はCOMPLETED、固定JST→UTC9時間差、names/type/field順保持|
|004|QSD/NTDの12byte ID3→各questionId/notificationId/N1/ASCII3、distinct response layout|
|005|search999999へempty effective1/50を受理、canonical原page不変|
|006|page0/layout/type/size49/record不足を型別拒否、NPEを不整合拒否の代用にしない|
|007|質問UNANSWERED/通知ACCEPTED-RECEIVED ID3を受理、target4/typed data違い拒否|
|008|四layout NUL/一byte不足/通常unknownZZZREQ01固定拒否、null境界、query全nullは先頭だけで停止|

期待はUI236 offset/長さ・明示field表/固定9時間差・typed入力の独立後条件から定め、Production encode/canonicalをexpected生成に使わない。一Source全一physicalの全counterを測るがbackend正常/残null/dispatchは未実行のまま不足を残す。SourceMainP01301/TestUNKNOWN、主費用同leaf・新群.5/2/4pp cap10/event3127予定、実0確認後14658 whole8/1を一回→14660独立XML/FES/真正終了/原ENV/全input-Jar/static14224/一CRC/八metadata反例/counter・owner照合。JDK25.0.4/Platform1.13.4/JaCoCo0.8.15・outer180秒。新Main/Test/fixture0・旧Source/exec合算0。結果2736へhash/command/time/環境/input/実際/未完を記録、正式/工数null/QA051final/全F03-451/HOLD維持。
