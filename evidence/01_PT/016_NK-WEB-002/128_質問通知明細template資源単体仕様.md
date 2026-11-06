# 質問・通知明細 template resource 単体仕様

NK-WEB-002/主WBS-P016-21・P016-23/P015-02参照費0。RD FUN012/013/QST006008/FUN108/NTF004005008・UI224236・SS313314332。MainD8のnormal web JARと同byteのquestions/detail.html・notifications/detail.html/shared layout。PT_DEFAULT、PMO963/event3997原1/3/6cap8。直近QuestionMutationRequest.applyは具体DBサービス依存で未実行、当resource試験に代替合算しない。

固定UI236 map/Optional fixtureだけでSpringTemplateEngine/MockServlet WebContextを動かし、Production Javaはclasspathへ入れない。全14method/23描画、USER/ADMIN・質問3stateと空/有回答・通知全5state/optional4日時・削除済body/answer/link非表示・エラー・notice null/空/有・確認formのchecked/errors/id/operation/action/method/hidden属性・backlink/deferredJSを実DOMで独立literal assertする。method/caseは下表、期待値はProduction model/rendererから作らない。null/invalid型入力等は既projection/formの責務であり当resource型契約外、再送・並行の実業務保証をしない。

確認フォームも送信しない。Synthetic operation UUIDとCSRF placeholderは一時context/DOMだけ、実session/key/tokenを使わず、snapshotのhidden値は永続化前にREDACTEDへ置換する。raw rendered formを保存しない。保存物は派生redacted DOMとして明示し、原HTML byteそのもののsnapshotとは呼ばない。postは全23でsynthetic値不在を独立確認する。既SDK依存をexact sha固定、ApplicationContext refresh/実ServletContainer/HTTP/DB/JMS/VM/Root/鍵/held4を起動しない。

sharedresource工具002の明示detail routeとinput004、prepare/static→Git固定→一回JUnit/独立post。Java counterはHTMLに非該当/nullであり100補完/除外/旧exec合成0。Main正常20112/六SB20114は再演しない。結果129/manifestへ時刻・環境・実command/source/exit/XML/派生DOM/hash/BUGを保存、fresh実終端後APIで群末結合。全MVC/Browser/CSRF/token資格/送信・受付/全451/正式1964/53/歴史17/190/工数nullは未受入のまま。

|Test ID|method|
|---|---|
|PT-WEB-DDOM001|questionUserUnansweredReadOnly|
|PT-WEB-DDOM002|questionAdminEmptyAnswer|
|PT-WEB-DDOM003|questionAnswerEscapesText|
|PT-WEB-DDOM004|questionErrorHidesAnswer|
|PT-WEB-DDOM005|questionConfirmationUncheckedAndErrorsEscape|
|PT-WEB-DDOM006|questionConfirmationCheckedAndNotice|
|PT-WEB-DDOM007|notificationReceivedAndProcessingTimestamps|
|PT-WEB-DDOM008|notificationCompletedAnswersAndLink|
|PT-WEB-DDOM009|notificationErrorFields|
|PT-WEB-DDOM010|notificationCancelledFields|
|PT-WEB-DDOM011|notificationDeletedMasksBodiesAndAnswerLink|
|PT-WEB-DDOM012|notificationConfirmationBothValues|
|PT-WEB-DDOM013|optionalNoticesNullEmptyAndText|
|PT-WEB-DDOM014|backLinksAndDeferredOperationScript|
