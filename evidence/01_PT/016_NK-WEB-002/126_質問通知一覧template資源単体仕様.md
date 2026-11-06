# 質問・通知一覧 template resource 単体仕様

NK-WEB-002 / 主WBS-P016-22、P016-20/P015-02参照費0。RD FUN012/QST006008/FUN108/NTF001002003008、UI224236、SS313332、questions/list.html・notifications/list.html・fragments/layout.html。Main D8正常web JARから抽出した三資源をrepo同byteへ照合する。Production Java JAR/classを試験classpathに入れず、既16/14ProjectionTestの成功再演・exec合成0。

PT_DEFAULT、着手957ではなく959/event3992、原1/3/6pp cap8。ローカルSpringTemplateEngine3.1.5/SpringEL7.0.9/Thymeleaf WebContextをmock Servlet request/responseへ結合、ApplicationContext refresh/servletContainer/実HTTP・DB・JMS・VM・Root・鍵・実sessionstore・held4は起動しない。installed ServletAPI6.1・Jsoup1.23.2等はinput001でsha固定する。自己所有compile/JUnit/DOM出力のみ。

FixtureはUI236のrow/filter/page schemaを明示したliteral map/Optional。expectedをProduction projection/engine出力から生成しない。正常row/page/count/owner/filter一致を手点検、invalidは意図的にerrorを付け結果無し。全12method、各renderの原HTMLをTestID付きで保存する。empty/records、USER/ADMIN owner列、invalid/valid errors、selected states全4/notification types全4、prev/next有無、NFC済keyword/date/username、ページ中間50行、escapeを実DOM値で確認する。共有layoutのhead/css/nav/login-role/logout postも実資源fragment解決で照合。submit/CSRF・controller・Browser/backend統合は未受入。

HTMLにJava LINE/METHOD/CLASS/BRANCHは存在しないため数値を100へ補完しない。resource条件vector/DOM実測を別記し、Java Main四100は既単一source/run証拠と分離する。snapshot/環境/command/開始終端/Git/source/exit/XML/hash・静的結果は127とmanifestへ保存。null・未知状態等の入力拒否はprojection/form既PTに属し、このrenderer単体から再送/認可/NPE安全を主張しない。正式1964/53・歴史17/190・工数null/新leaf0/技術source52は不変。

|Test ID|method|
|---|---|
|PT-WEB-LDOM001|questionEmptyUserView|
|PT-WEB-LDOM002|questionAdminRowsEscapeText|
|PT-WEB-LDOM003|questionUserRowsHideOwner|
|PT-WEB-LDOM004|questionInvalidShowsIssuesWithoutResults|
|PT-WEB-LDOM005|questionPagingAndFilterPreservation|
|PT-WEB-LDOM006|questionAllStateOptions|
|PT-WEB-LDOM007|notificationEmptyView|
|PT-WEB-LDOM008|notificationRowsEscapeAndPreserveOrder|
|PT-WEB-LDOM009|notificationInvalidShowsIssuesWithoutResults|
|PT-WEB-LDOM010|notificationPagingAndFilterPreservation|
|PT-WEB-LDOM011|notificationAllTypeOptions|
|PT-WEB-LDOM012|sharedLayoutLinksAndLogoutAreRendered|
