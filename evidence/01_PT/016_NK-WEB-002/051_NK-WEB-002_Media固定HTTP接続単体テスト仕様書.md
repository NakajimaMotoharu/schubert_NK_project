# Media固定HTTP接続単体テスト仕様書

2026-10-03。Program NK-WEB-002/NK-MED-001、S3/D05のWeb業務assembly依存。RD FUN-005～007/FIL/AUT/PER、UI221/223/232/235/237、SS313 §8・314・323・333 §8～11/351/352。対象候補はMediaControllerの5endpoint、MediaMvcConfiguration、MediaResponseDecoderの検証済wire値投影。新規未実装TDDの失敗は障害に算入せず、実装済の仕様違反は修正前915/必要916へ登録する。

接続: closed SessionPrincipal→fixed AUD/VID/MED facade→既存全wire検証→要求type/logical ID/disposition再照合→process単一MediaRangeService/held secure FileSource→HTTP。1 GET/HEADごとにAPI照会し、session/descriptor cache・Web業務DB・Caddy direct file・file全体byte[]取得は使用しない。独立wire fixtureはUI232/235絶対byte offsetによる手組立、HTTP body/Rangeは固定公開合成fileから期待sliceを指定する。Production methodでexpectedを作らない。

| Test ID | 事前条件・入力・操作 | 独立期待値/根拠 |
|---|---|---|
| PT-MED-HTTP001 | 5固定URL/USER・ADMIN、GET/HEAD、0000/0200 | IF009 I/A・IF012 I・IF016 I/Aの全request byte、fresh UUID/context、200/Content-Type/Length/Disposition/nosniff/private no-store。HEAD body0、GET固定file全文、API各1回 |
| 002 | inlineなし/0-0/開始末尾/suffix/複数先頭/不正/overflow、attachment Range | SS333と固定file長から200/206/416、Content-Rangeとsliceを手で算出。download200全長、HEAD body0。ETag/Last-Modified無し |
| 003 | 不正Audio ID/0/13桁/符号/未知文字、logical ID空/過長/UTF8超過/制御/末尾space、e＋combining accent | 不正は400/send0/file0。SS313 NfcByteLengthで正規éを独立期待値とし電文・descriptor・Range照合一致/200。constructor/null/別Principalはinvariant拒否で成功扱いしない。未使用queryは既存互換どおり無視し権限/ログへ使用しない |
| 004 | API各error code/timeout/JMS、不正header/correlation/context/予約byte/descriptor | SS351分類、0103=403/0104=404/9000=503等。decode失敗503/file0、raw例外/pathをHTTPへ出さない |
| 005 | 正常wireで別logical ID/type/path/disposition/MIME応答 | 要求/descriptor再照合で503/file0。projectionがAPI認証・secure open代替にならない |
| 006 | API0102、GET/HEAD、encrypted sessionとsecurity context | 401/session/context/表示snapshot失効、mediaへ302しない、file0/再送0 |
| 007 | open前I/O、response未commit/commit後I/O/client abort、20stream保持/21件目 | 未commit503、commit後追加応答0/固定IOException、close/permit解放、BUSY Retry-After1。既存stream取消/成功捏造なし |
| 008 | 明示MVC compositionで全5URL/HEAD/POST/unknown route/unauthenticated境界 | HTTP route/メソッドに沿う要求のみ、media承認済みsecurity gateを維持。部分MVC成功を全Webreadyにしない |
| 009 | 多thread/各役割/5route・個別Range | context/UUID/body混線0、pending0、send/reply buffer全0、DB lockをstreamへ持越さない |
| 010 | decodeVerifiedのnull/foreign layout/error/success/video metadata/不正typed入力 | raw decoder既存goldenと同一descriptor契約。private wire Resultのみ受理、要求に対応しない投影拒否、秘密/pathのtoString露出0 |

予定command: 既存6module reactorで関連codec/Resource/Web config/API management/media・wire・session suiteを選択し、Spotless/strict javac/NullAway、SpotBugs6、JaCoCo line/method/class/branchを採取する。source固定後の全回帰triggerは全Web起動契約へのsecurity/controller接続変更群。過去PG433 full結果を新sourceへ流用しない。

状態: 仕様準備、code/試験未実装・not-run。実command/時刻/branch/source/exit/coverage/BUG/hashは052実行結果とsanitized manifestへ保存する。全scope同source/native100%・親/Web/Caddy/CHR/DONEは未受入、正式認定PT-WEB-20260925-24/1964PT/53scope不変更。fixtureは公開合成値だけ。実原本/Backup/token/key/credential/passwordをGitへ保存しない。
