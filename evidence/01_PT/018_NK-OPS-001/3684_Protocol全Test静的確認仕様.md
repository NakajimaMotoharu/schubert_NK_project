# Protocol全Test・静的品質確認仕様

NK-OPS-001/F03、411/451/SS311352354。normal Main7aed不変、protocol moduleのtracked regular Java Test全25をindex metadataで固定する。既golden三の再資格/source修正を引き継ぎ、まだ未照合のmodule全Test静的範囲を一度確認する。原2/5/9pp cap10、F03 CONTRACT_AUDIT/SOURCE_REQUALIFICATION。

正規PMD7.28 record patch/Checkstyle14.3/GJFの既pin設定を変えず、normal protocol JAR/JUnit1.13.4/jspecify/JDK25と明示file-listだけを使用。formatはdry-run・変更0、processor/元Test compiler/JUnit/Test/fixture/製品/DB/JMS/VM/Root/native動作0。各engineのclass-initからProduct初期化が無いことを確認する。固定SDK/rule hash・全25Git/source hash・stderr/exit/reportを独立postで照合し、発見件数はraw/適用性未分類/個別非該当/実違反を分ける。未分類を0や合格にしない。

実違反はBUG/YKTを修正前起票し、意味/期待値を変えない是正と必要な元全class PTを次群へ分ける。既不変成功・全module回帰を確認だけで反復しない。既956待ち索引は修正前のsnapshotとして保持、3Testの以後修正は個別source/runへ対応する。

候補照合（加点0）：JmsRequestReplyClientTest.await(release)はcallerの有限await/getとfinally releaseで所有される既許可helper。新障害と即断せず、元8の確認再演や架空のtimeout期待値を作らない。WebLogDispatcherの全Testは実DB/Brokerとheld WebStartupExceptionを含むためHOLD、Reportのinvariant caseも既元Testに存在し、同じ期待値の新fixture置換で受入を作らない。ApiObservation/ReadOnlyAttemptはheld TemporaryInfrastructureException依存なのでwhole動的HOLD。

scopeはprotocol Test静的だけ。新Test/PT/coverage/unique/whole/leaf加点0、正式1964PT/53scope・工数null・全HOLD不変。
