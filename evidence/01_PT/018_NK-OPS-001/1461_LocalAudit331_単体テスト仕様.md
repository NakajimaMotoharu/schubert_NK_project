# LocalAudit331 primitive logger/terminal graph PT仕様（実装前）

Program NK-MSG-002/REQUEST local producer、class WebRequestLogProducer.local/metadataInvalid（共通口はcompleteにも適用）。RD MON003/UI235252/SS312351354、BUG1601/YKT1354/SSC331、cost owner=485実物のWBS-P006-03。新群ORDINARY_LOCAL_AUDIT_GRAPH/event1663の着手前低.2/標準.7/高2共有週次pp（未較正）、既common Web portの再製造/二重費0、原-v4/旧群開始見積は変更しない。fresh65残35/reset1793082864/secondarynull/券0、実token/専有費null、モデル指定と実設定は区別する。

## 設計先行と範囲

SSC331は台帳を先行し三SSへ内部例外詳細を横断反映。design-only source d721e1533/PR195→main8968f2770を通常merge/remote確認済み。Main/ツール/証跡はmainへ混入0、branch protection/自己承認迂回0、PR添付はcap100で一回失敗（URLは本書/台帳へ保存、既添付削除/回避/再試行0）。新business/RD/UI/HTTP/wire/DB/owner/backoff/権限・DIF変更なし、QA不要。

PT_DEFAULT：pure System.Logger/Runnable/DataSource proxy、公開synthetic key32byteのcodec constructor/closeだけ。metadataInvalidは識別子/DB/JMS/暗号化/ネットワーク/VM/Root/原本・鍵取得を一切発行しない前提をカウンタで検証。通常complete/REQUEST/projectionは既domainで回帰する。拒否対象の再試行/代替PTではなく、PTALT代替完了0/全HOLDを維持。

## 独立oracleとTest ID

`LocalAuditGraph331Test`四method、SHA256 `13160c4d855d7b08b0192d01dd721580ef6bab6a553981ec5162c3aafce65a1c`、全旧Test/Main2d4633fb2固定。formatter79275終了0、管理3/pyflakes0。期待Errorは固定作成したobject identity、callback/DB/identifier/JSON値・順序はliteral/tableで作成する。Production methodからexpectedを生成しない。System.LoggerのString default methodはJDK25.0.4のjavapでResourceBundle/parameters=null、一回のabstract log呼出だけと確認し、fixtureが余計な操作を予定反例へ誤認しない。

|Test ID/method suffix|入力/操作|独立した期待値|
|---|---|---|
|331001 LoggerGraphSignalsOnceBeforeOriginalFatalWithoutAnyProjection|logger isLoggable/logのRuntime cause/suppressed/JMS linked/SQL next→固定Error、metadataInvalid|check1、log0/1、terminal1、DB0/identifier0/unknown0、check→log（存在時）→terminal後に同一Error|
|331002 TerminalGraphCannotBecomeFixedOrdinaryCatalog|disabled logger又は普通logger Runtime、terminal Runtime graph各四edge|terminal1後にcallbackの同一Error、普通catalogへ縮退0、DB/identifier0|
|331003 CallbackThenLoggerGraphPriorityAndAliasesAreIndependent|logger graph Error＋callback ordinary/別Error/same object graph|callback graph Error優先、callback非fatalならlogger Error、aliasも有限・同一object、terminal再試行0|
|331004 OrdinaryCyclesDisabledSuccessAndDirectErrorRulesStayUnchanged|正常/disabled/非fatal cycle・同一Runtime/両ordinary/直接logger Error/直接callback Error|正常log通知0、disabled/ordinary通知1、callback ordinary時fixed IllegalState（cause/suppressedなし）、直接logger Error通知0/直接callback Error通知1の既優先|

全ケースでDB/identifier0とunknown operation0、logger/terminalの回数と順序をError identityより先に検査。PRIVATE_ provider canaryをJSONへ出さず、正常metadataのtimestamp `2026-10-22T00:00:00.000Z`/WEB/INTEGRITY_FAILED/UNKNOWN/WEB_REQUEST_LOG_METADATA_INVALIDを明示assertする。codecはcaller fixtureがTWRでclose、producerは取得していないDB/JMS/外部serviceをclose/rollbackしない。

## 実行前固定

既PYTHONPATH三path＋`python3 -B tools/quality/pg6646_local_audit_selected.py PHASE`。red=PG6646（宣言16件8suite、Web停止時の実14/6・F3を予測、後段2not-run）、read-redは予定331001/002/003の`expected: <true> but was: <false>`だけを元XML/原終了1/phase0,0,1/source/archiveと照合し、331004既後条件はPASS予測。失敗の意味が異なる/fixture不明操作があれば原反例へ加算しない。

原反例確認後だけ必要一Mainの局所PG、全新/旧Test bytesを固定。green=PG6648/31件11suite（全六baseline12/7＋新4/1＋既producer9/1＋projection graph3/1＋Web port3/1）。真正0後だけqualify-green=PG6650で原六Jar/XML/all8511667/source/当counter/静的rawを照合する。全体宣言は現在4158/635＋新四method/一suite=4162/636の予定であり、原結果前にPASSや四100へ補完しない。関連callback横展開は必要scopeを調査/起票して既知関連群をまとめ、必要同source全体を反復しない。

現時点dynamic未実施・PG未実施。正式1964/53/個別17-190/工数null/QA051final/未特定PTALT/実VM等HOLDは保持。実行timestamp/OS/tool/branch/commit・実commandは元begin/manifest、期待/実際/BUG/SSC・evidence hashは原読取と後続実行結果へ保存し、失敗/未実行を加点しない。
