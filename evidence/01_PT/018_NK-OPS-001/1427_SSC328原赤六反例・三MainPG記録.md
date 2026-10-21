# SSC328原赤六反例・三Main PG記録

BUG1591/YKT1344/PG-D483、1424の独立期待、Testsource0416a76ef03135d3b14153221b4c33e55083bc3b/oldMain f39（全Main旧byte）。新九Testを変えずAPI/Webを順次一回ずつ実行した。

|原run/session|UTC|実XML/目的失敗|終了/phase|
|---|---|---|---|
|6534 API赤/88144|14:12:36.576426～14:14:25.348943|10件/6suite・F2（Auth cause/SQL next不伝播）、E/S/flaky0|1/[0,0,1]|
|6536 Web赤/65112|14:15:49.955731～14:18:09.667748|17件/8suite・F4（Session/Revocation next各2）、E/S/flaky0|1/[0,0,1]|

日付2026-10-21。先行format/testCompileは両0、compile/timeout/別例外ではなく `Expected java.lang.AssertionError to be thrown, but nothing was thrown` の指定六caseだけを原XMLで確認。各後段moduleはreactor停止によるnot-runで、合格へ加点0。両run同archive SHA `a02a4165bde8e5009661f31b48084d69530d46d68da842d9bee430bafa4732bb`、Test3file SHA一致/oldMain固定。API原manifest SHA `bd040bb70365d4a77279439a5decdb2c4506778d587c26aa76f6111bf11dbbe4`。Web含む全原hash/全保存XML/失敗methodは公開 `evidence/provisional/PG6536-jdbc-original-red-v1/manifest.json` SHA `82d258fe74ca5f71035408fc25054a0f5ebe4f0acf473083dbe25c5e42ead093` に一意結合。独立readerは終了0だが原PTは赤/失敗であり、PT合格の意味ではない。

修正は三Mainだけ計17行：Authの既suppressed順の後にcause/SQL next、SessionStore/RevocationRetryの既cause/suppressedの後にnextをFIFO追加。元Error早期throw/identity visited/入力例外の非保持/固定catalog/SQL・資源・再送順を一切変更せず、visited nodeはgetter再読しない。SQL nextは各nodeで一回取得・null時は追加しない。JMS linkedは当JDBC helperの責務外、他catalog1323の一括完了とはしない。

三Main以外/既Test/gates/全red Testbytesのdiff0を確認。formatter23488終了0、管理四件0、green sourceのguardはREDSOURCE0416a76の全Testbytes不変/正確三Main差分を要求する。greenは未実行、次clean commit/push→6538 green23/12一回→真正0後6540原8511667/六Jar/XML・static/当targetcounter。既domain/必要新source全体4082/617はその後へ残し、元4073や旧nativeから合成しない。

fresh used55/rem45/reset1793082864/secondarynull/券0。群1623 .3/1/3/原-v4固定、実N/T/専有費null。秘密/credential/DB/VM/Root/intent/permit/cohort操作0、正式1964/53/17-190/工数null/QA051final/PTALT代替0/全HOLDは不変更。BUG/SSC/YKTはgreen/必要品質まで未受入。
