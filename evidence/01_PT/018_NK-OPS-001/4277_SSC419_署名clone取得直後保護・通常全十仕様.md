# SSC419署名clone所有の通常PG/PT仕様

ReleaseSignatureVerifier.verifyは既null/長さ検査とpublicDER/元manifest/signatureの同byte clone・既Crypto/JDK Ed25519を維持する。key clone直後に外try、その内でmessage clone直後に中try、signature clone直後に既Crypto try/catch/finallyを置く。finallyはsignature→message→keyの逆取得順で一回ずつ消去、既GeneralSecurityExceptionのfatal graph/Error identityと固定IOExceptionを維持する。返却前のJDK未取得allocationの消去は保証せず、実OOMを起こさない。原public API/constructor/認可/署名format/鍵の固定根/結果/期限/電文は不変更、新operation portやprivate key/実署名/配備を追加0。既9Test全文は保持、新SIGN010だけ合成RuntimeException後に同instanceを正常再利用し、三copy消去/caller不変/pinned再利用/次回独立copy/call数2を固定publicRFC vectorで確認する。同source全10、RootNullAway/静的、sameexec default/raw target全命令行methodclassbranchを照合し、StorageIoException依存の未網羅を隠さずglobal451/正式へ算入0。

費用.2/.6/1.8pp・cap3、追加発見として元費用/904.85/SV/各群開始保持。原9の確認再演は行わず変更Mainの必要全10資格を一回実施。新定義はSIGN010一つだけ。ManifestにOS/JDK/source/branch/command/真正終了/64byte publicRFC signature・期待値/実際値・coverage・BUG3015/SSC419を結合、private key/実鍵/原本/配備なし。
