# Web7family固定ラベル値catalog PG/PT仕様

NK-OPS-001/RD171/UI252/SS311351 §6/10・411、PG-D597、WBS-P018-09/C07参照0加算、group1990。開始fresh26/74・1/3/6pp/cap10はPG8360/event1990へ固定。先行1762/8350～56の22成功は確認目的で再演しない。

## 必要依存と実装境界

既generic codecは明示契約どおりcaller承認済みのlabel値を借用し、keys/型を検証する。今後Web7familyを公開側へまとめる前に、承認済みSS351の値catalogをWeb内で確定する必要がある。WebMetricCatalogは固定gauge4/counter2/histogram1の名前・key・closed値を所有し、各Meter.Idの検証済みlabelを**immutable SDK Labelsへcopyして返す**。別preflight後にmutable registryを再読取るだけの方式は採用せず、後続のencoderはこのLabelsをmodel生成時に使うこと。当群はcatalog自体の依存製造/PT、まだexporter/endpointへ接続しない。

Route35は既HttpMetricContractの承認済みtemplateだけ、method10/status_class5、service/store WEB、pool state4、outbox status3、media_type3/mode3/status4を閉じる。任意raw path/user/id等を許可しない。例外messageは固定、nullをunknown/0へ補完しない。namespace返却はdeep immutable、provider Id/Tagの参照を保持しない。SS/Bootstrap/API/POM・既codecは変更しない。

## 独立14 Test ID（WebMetricCatalogTest、未実行）

|ID|入力/期待・独立根拠|
|---|---|
|WEBCAT001|gauge4/counter2/hist1の全七名前とexact key sets、SS351から固定literal|
|WEBCAT002|HTTP counter全35×10×5=1750、fixture route SHA1777c471＋独立method/status一覧で全Labelsを確認|
|WEBCAT003|Timer35 template全て/二keys、HTTP counterとのkey差を独立fixtureで確認|
|WEBCAT004|pool4/outbox各3/media3の13gauge系列、固定literal値/key|
|WEBCAT005|media bytes三type×三mode×四status=36、固定一覧|
|WEBCAT006|未知metric name/別role nameを固定IAEで拒否・入力値がmessageへ不在|
|WEBCAT007|各labelの未知値・raw route・username風state・lowercase enum・未知status等を拒否|
|WEBCAT008|全七familyのmissing/extra keyを拒否|
|WEBCAT009|duplicate tagsの実key/Id identity独立assert→拒否|
|WEBCAT010|null Id/name/tags/Tag/key/valueをAPI境界で拒否、NPE正常化なし|
|WEBCAT011|source tag list/可変Tag値を返却後に変更してもSDK Labelsは元copyを保持|
|WEBCAT012|返却namespace map/setの変更拒否、以後の返却値/labelsに非影響|
|WEBCAT013|provider RTE/Error identityを保持・原文formatなし|
|WEBCAT014|有限64並行callで各固定Labels/namespaceを確認、join10sec・sleepなし|

期待集合はSSのliteralと既独立route fixtureから組み立て、production enum/catalogからexpectedを作らない。fixtureからの正常domain vectorと全field negativeを対にする。14/1、F/E/S/aborted0、新Main1の実四100・静的0・正常六/全physical-owner責務を要求。SDK Labelsの公開accessorでのみ確認、private反射/coverage偽装なし。

## 証跡・未受入

source固定後PG836x normal六/PT0→一回original14/1→独立四100/CRC0/session1/静的/metadata→全physical/source/所有→1764へ、command/OS/JDK/日時/branch/source/exit/input/expected/actual/XML/coverage/hashを元slotと公開manifestに保存。現在PT/coverage UNRUN、実装済み違反は修正前BUG/YKTへ。

catalog完成は実公開/accepted metric全体の受入ではない。後続はこのLabelsをmodelへ直接渡すcodec接続とDEBUG/STANDARD pure policy、actual endpoint/VM/Root/DB/native/鍵/配備/拒否未特定はHOLD。formal1964-53/原190新受入0/工数null・QA051final/whole451未受入を維持。元/v4/v5/共有枠と専有費を混同しない。
