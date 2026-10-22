# 次ordinary候補・公開相関値codec境界（準備、未着手）

6784当source3c5のMain/Testは全体中固定する。本資料はその原品質/trace完了後の独立候補だけで、新PG/PT実行・受入・見積減額0。直前全d549の該当Main hashは現sourceと一致、当4197原counterで再照合してから着手する。API管理のdefault bind/内部停止結果gapは別候補として保持し、実Web全体中に改変しない。

## 安全・独立性

対象はメモリ中の公開相関文字列/recordのconstructor/consumeだけ。既Testに手書きされたUUID/時刻/固定hexのliteralを使い、ファイル/DB/SSH/VM/サービス/current/Unit/署名/intent/permit発行・退役・回収/native資格・failed cohortへの操作は呼ばない。コード上もclaimsは起動/削除/DB lock権限でないと明記される。資格情報や現環境のrun/boot/epoch値を取り込まず、公開テキストの不正byte/末尾/相関不一致の拒否・入力erasureだけを独立検証するPT_DEFAULT候補。拒否対象を判定する試し実行や別routeによる回収ではない。scope/command/fixtureに変更があれば改めて事前判定し、未確認の安全条件が必要なら保留する。

## PGレビュー候補と不足入力

Mainは既承認のvalidation/parse/固定message/owned erasureが正しく、現時点の変更必要性を発見していない。PGは省略でなく、その正しさを独立reviewし不要改変を避ける判断を着手時に記録する。以下は現原XMLのmiss分岐から旧Testを横断して特定した未検証入力で、品質達成を先に宣言しない。

|対象/owner|既原残/独立候補入力|独立期待・非該当|
|---|---|---|
|StartupLaunchRecord/ P018-03|2B：ASCII走査の正のDEL127、行数は正しいが最終空行にXを置く（GOLD+X）|IOException `startup launch unavailable`/cause null。既255はsigned -1でlow側、末尾LF欠落は行数側であり同じ入力でない。新一Testの二vector、正常/全field/null/hashは既四Test固定。DB/ownerを認定しない|
|CleanupWorkerRequest.Expiry /P017-07|6B：constructorのNIL run・activation・boot・不正broker grammar（他は有効literal）。普通/skip双方のDEL127と同じ行数のtail X|IllegalArgumentException `cleanup request invalid`/cause null、consumeのowned bytesは全zero。constructorだけのimmutable dataは書換え0。新二Test、既epoch NIL・broker all-zero・相関/時刻/skip priorは固定既Testで非重複|
|CleanupFailedBackupRequest /P017-06|3B：DEL127・tail X、constructorへrunが別の独立BackupFailureSnapshotを渡す（両snapshot内pair自体は同run/step/orderで有効）|IllegalArgumentException `failed cleanup profile invalid`/cause null、consume所有byte erasure。新二Test。既U64+1のbackupEnded入力は既cfreq003に存在するので重複追加しない。新直接constructorのrun mismatchをparser同run生成の試験で代替しない。`verifyLatest`/receipt/回収/DB読取は呼ばない|

SS343/SSC104/111/117/124/137、既CREQ/EREQ/CFREQ/LAUNCHに追跡。expectedをProduction encode/consumeから作らず、既手書きfixture又は同内容の独立literalを使う。fixture再利用でprivate field反射しない。public fail literalは新Testへ手書き、構造体入力も公開constructorで作る。Null/正常/境界等の既oracleを一byteも変更せず新Testファイル三/新method五を予定（発行前に既declarationの実数へjoin）。Main/gates不変なら全物理1669完全同一を原Jarで確認する。

着手順：現Web全体/原品質trace→当counter再認証→主P017-07＋componentP018-03/P017-06（各481/484実leaf確認、親/共有費二重加算0）・開始予算固定/PG判断→新三Test五methodと仕様固定→関連まとめdomain一回/独立原資格→必要当source全体一回/品質trace。未実装Test初回赤はTDD、実装済みが承認期待に違反したら修正前915/916/必要SSCを起票。旧成功の算術加算0、global/F03/正式1964-53/個別17-190/工数null/QA051final/PTALT代替0/全実環境HOLDを維持し、通常候補完了だけで停止しない。
