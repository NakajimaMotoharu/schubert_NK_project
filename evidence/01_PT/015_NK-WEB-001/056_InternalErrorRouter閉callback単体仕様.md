# InternalErrorDispatchRouter 閉callback単体仕様

NK-WEB-001/WBS-P016-24、FUN/AUT/TST・UI221222226・SS313SSC047/314/352/PG-D116、PT-WEB-ROUTERPORT001..010。982/event4015原1/3/6pp cap8。MainD8 whole physical1を自己所有callbackだけで実行する。ErrorMvcTestの全security/session/MVC fixtureは実行・切出しせず、拒否境界探索を行わない。既保持4classと実errorchain/DB/VM/Root/permit/鍵/認証発行から独立する。

1. Constructor二nullとinit config nullの契約。
2. business→error initの順序、同じconfig参照、正常終了。
3. business init Servlet/Runtime/Errorがそのまま伝播し未開始errorへinit/destroyしない。
4. error init Servlet/Runtime後にerror→business destroy、SS313既例外順位維持。cleanup失敗とbody失敗を正常へ変換しない。
5. destroyはerror→business順、最初が失敗しても後者を実行、既finally例外順位を固定oracleで確認。
6. REQUEST/ASYNC/FORWARD/INCLUDEとERRORのpath不一致はbusiness callback一度、ERRORかつ/errorだけerror callback一度。実業務や認可を実行しない。
7. ERROR/errorにWebRequestContext欠落・誤型があればcallback未実行/失敗、正常dataのみerror callback。trusted contextは公開docIP/固定UUIDの表示用値。
8. 各callback IOException/ServletException/Runtime/Errorの同一性を保持、finallyで空ThreadLocal contextの参照を破棄。Throwableを認証や成功に扱わない。
9. null request/response/chain、非HTTP request/responseを明示拒否しcallbackゼロ。invalid precondition外側でのclearは合格条件へ創作せずTest自身がcleanupする。
10. 2worker8request・10秒join、各空context/request/trace非混在・終了後認証null。

SDK SecurityContextHolderは新しいTest JVMだけ `-Dspring.security.strategy=MODE_THREADLOCAL` に固定し、empty SecurityContext以外を保持しない。Authenticationを作成・setしない。既service/アクセス経路を変更しない。static SDK bytecodeでThreadLocal.removeを照合する。Production source/clear method以外の実session/authfilterは初期化禁止、JDK/Spring metadata syscall数は未計測null。

独立oracleは明示順序配列/Filterとrequestの参照同一性/固定例外オブジェクト/入力dispatcher表、Productionからexpectedを生成しない。profile077/shared012、prepare20500/static20502→Git固定→20506全10/一exec/全physical/四100/CRC/post。実行環境/JDK25.0.4/inputHash/source/command/終了/coverage/BUG/証跡は結果057へ保存。既正常Main/SBを再確認目的に再演しない。全SCR090/実chain/CHR/native/451/個別leafは別未受入。
