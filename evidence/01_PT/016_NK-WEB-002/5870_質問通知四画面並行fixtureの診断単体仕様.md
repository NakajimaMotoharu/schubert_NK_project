# 質問・通知の一覧と詳細の並行投影試験

NK-WEB-002、UI236／SS313・354、SCR020～023、BUG-3929・YKT-2997。

| Test ID | 独立期待値 |
| --- | --- |
| PT-WEB-NLIST014 | 8個のreader表示と固定行ID 12。別のcallerの表示が混ざらない。 |
| PT-WEB-NDETAIL008 | caller表示と元表に固定した通知状態の表示ラベル。 |
| PT-WEB-QLIST016 | 8個の異なるcallerと各owner行が一致し、最終頁の次リンクは空。 |
| PT-WEB-QDETAIL008 | caller、質問要約、提出日時1970-01-01 09:00:00と未回答表示が元の期待に一致。 |

各試験は2 worker、合成8件、Futureと所有停止各10秒。元の処理が失敗したときは停止失敗を抑制例外に残す。再発防止は既ViewFixtureWorkersTestを参照。selected normal PTとして元Java 25範囲を固定し、テストXML・終了・生coverage・製品入力を保存。実HTTP・永続化・外部資格への接続は要しない。
