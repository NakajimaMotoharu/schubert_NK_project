# API/Web例外graph9・静的PT設計レビュー

## 判定・対象・保全

2026-10-25、23:42 JSTの保存文書照合。STATIC_PT_DESIGN_REVIEW_COMPLETE（既存9件の文書対応点検を完了。動的受入完了ではない）。PT実施=NOT_EXECUTED、動的証跡=HOLD、拒否範囲=HOLD_SCOPE_UNRESOLVED、coverage/native/正式受入増分0・工数率null。新しい入力・fixture・Test ID・ハーネス・製品変更なし。JUnit/Maven/javac/preflight/PG9774/9776/実起動・接続・収集・VM/Root/鍵/DB/permit/既process操作を実施していない。

適用指示は work/PMO/hourly-monitor/user-static-review-20261025.txt の利用者方針。新しい文書レビュー群STATIC_PT_DESIGN_REVIEW_GRAPH9_20261025（event2223）は低.25/標準1/高3pp/cap10で着手前凍結、旧PURE群2222の.5/2/6、原見積/v3/v4/v5/不明実費は変更しない。主P01805/関連P01806、参照追加費0・専有配賦不明。fresh used12/残88/reset1793513544、現在窓を使用し旧累計上限へ戻さない。

保存HEAD ce726cc4ae44c17a89f8b336647f4e3be1878838/origin同一、Production source e598a81bb4200b4e4930278b31479ff927aa025f。Main二件/Test三sourceは全て当sourceのGit byteと一致。未追跡1974/9772原manifest・工具を保持し再実行なし。既9772 manifest SHA-256=64d513b58d849186660775d644c821dc5f16627821f00f9f83edc3abcb876548 は準備照合exit0/PT実行0/予定9件3suiteであり、拒否対象又は実行成功とは断定しない。22:18の拒否はPMO伝達事実、具体的操作・command・Test IDは未特定。こちらで拒否を再現・探索していない。外部job/VMの現在所有・生存は今回観測しておらずHOLD、停止したとも推測しない。

## 読取資料の同一性・参照略号

正本設計はローカルtracking ref origin/main=8b91944df5820535e23ba2469740f1c0aa94c447（今回fetchせず、remoteのそれ以降の更新有無は未確認）。対象SS四文書はそのGit byteと一致、当branch差分の別353をレビューへ取り込まない。RD/UI全体再監査や他Main/callerの検査は対象外。表のA/W/T/B/Cは以下のrepo-relative pathとその1-based行番号を指す。

| 略号/読取対象 | path | SHA-256 |
|---|---|---|
| A | src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/error/TemporaryInfrastructureException.java | fdd08bb7a96244c769e1c2656fad0886f71c46d5d27ef45e86efc4884b7457b4 |
| W | src/schubert-nk-web/src/main/java/dev/codex/schubert/nk/web/bootstrap/WebStartupException.java | 4a113031803c8bed2132f488f2a82b19f4e71695e0134fa417050f2ab1c53bfd |
| T | src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/error/TemporaryFailureGraph329Test.java | 9cbba6faab34b87e84865fd1102266c801e650bc0ad3ea0bf7f795461d5503fa |
| B | src/schubert-nk-api/src/test/java/dev/codex/schubert/nk/api/error/ApiStartupGraph330Test.java | 423473fc63459aa8cba5f2e5cfa6820c2c2cdfa66d80877136a35465a1ba0be2 |
| C | src/schubert-nk-web/src/test/java/dev/codex/schubert/nk/web/bootstrap/WebStartupGraph330Test.java | 585d63d018d3fb827154a6ffcb5986dffe5f2172443b818a086eabea8175d60c |
| 1430 | evidence/01_PT/018_NK-OPS-001/1430_SSC329_原五反例・共通分類PG仕様.md | f73e453686a80ae9a7a446512355c012dbec507cad39247b2bf77fdc14c5510b |
| 1437 | evidence/01_PT/018_NK-OPS-001/1437_SSC330_pure_port・PG判定仕様.md | 93586cadf397f78159e825bc88823b35e0b93bdfd34b1f20d4d52e5e3eb6cc94 |
| 1974 | evidence/01_PT/018_NK-OPS-001/1974_API_Web純粋例外graph_単体テスト仕様書.md | 8cb0ea3d58f3fd70cd97c7a26054204fd04dd63b4cd4243f50412710a47e20cc |
| SS312 | documents/300_SS/310_アプリケーション/312_処理sequence・method・例外・transaction設計.md | 7fc9bb837b9669f301c4c8d1b0b93ea1d680fd6c30e34b7f754e5210beb3765b |
| SS324 | documents/300_SS/320_メッセージング/324_Outbox・Inbox・冪等性・再送設計.md | 2bc99fd66ca1121a1ab4ae44e97aab96b52d4cf4c8145f6a425f89c7b07ce774 |
| SS342 | documents/300_SS/340_batch・基盤/342_Caddy・systemd・PostgreSQL・Java設定設計.md | 3775cb1faf0b96572f4913d06682100da1861f1d364a66f4118b03e27abf4b82 |
| SS354 | documents/300_SS/350_運用・品質/354_PT・IT試験観点詳細設計.md | edfd716ed55ff4b72739ed2e142c1dd7812a9682ba24895a765c1934b49bb0ae |

## 9 Test IDの対応matrix

全行の静的判断は「記載した既存fixtureとassertionが独立期待値に対応する」。PASS、全分岐実測、承認済み実行免除とはしない。各fixtureのError/ThrowableはTestが先にnewした元object、固定文字列は1430/1437由来であり、production classifierをexpected生成に使わない。表の残証拠D1=当sourceの正式許可された真正XML/終了code/非skip・非abortedと時間内帰還、D2=当session/CRC/全対象counter、D3=必要caller/owned resource後条件・全品質（この群では実施しない）。

| Test ID | 承認要求/独立期待値出典 | Main分岐・既存fixture | assertion行/静的判断 | 残動的証跡 |
|---|---|---|---|---|
| PT-TEMP-GRAPH329001 | SS312:19/SS354:43、1430:13 | A16–39。SQL root/alias cause・suppressed next・next→rootの循環/重複、後からnext.causeに元fatal | T21帰還、24–27元fatal identity、28–32列挙edge保持。有限graphへのvisited構造と対応、全getterの任意実装までは主張しない | D1/D2。列挙外edgeの非破壊/実callerはD3 |
| PT-TEMP-GRAPH329002 | SS312:19、1430:14 | A18/24–37。直接Error、root直下cause Error/suppressed Errorとnext経路、causeなし/nextのみ | T42–45 direct、49–52 cause、56–59 suppressed、62–65 nextのassertSame。既fixtureの順位を確認する設計であり階層全体のcause絶対優先ではない | D1/D2。任意階層競合の網羅は未証明 |
| PT-TEMP-GRAPH329003 | SS312:19/SS324:3、1430:15 | A11–13/17/23–39。null、非fatal Throwable/SQL、新catalog | T70–75 null/非fatal、76–79固定message/cause null/suppressed0。新catalog初期状態のassertionであって任意の後日変異を禁止する試験ではない | D1/D2。callerがproviderを捨てる境界はD3 |
| PT-API-STARTUP-GRAPH330001 | SS312:13/SS354:41、1437:9 | A17–39。JMS linked→SQL next→cause fatal、linked/suppressed/cause/self-next混合cycle | B22–28 chain/identity/edge、36有限帰還、38–45元fatalと列挙edge。新接続/起動を行うfixtureなし | D1/D2。実readiness/closeはD3 |
| PT-API-STARTUP-GRAPH330002 | SS312:13/SS342:11、1437:10 | A11–39。直接Error・cause/suppressed/linked、空JMS/SQL/Throwable/null/固定catalog | B55–58 direct、63–66 cause、70–73 suppressed、74–85非fatal/null/固定診断。linkedの到達は001にもあるが、全ての深さの競合順位を証明しない | D1/D2。深さを跨ぐ全順位・業務readyは未証明 |
| PT-API-STARTUP-GRAPH330003 | SS312:15/SS354:41、1437:11 | A43–53。same/distinct object、suppression無効Runtime/Error・primary causeとsecondary fatal | B92–95同一/別object、99–120disabled側fatal順位/普通帰還/suppressed0、121–126null、helper129–142。無効時にprimary graphを先に分類する順序と対応 | D1/D2。全caller finally/TWR・完了解放はD3 |
| PT-WEB-STARTUP-GRAPH330001 | SS312:13/SS354:41、1437:9 | W13–34。JMS linked→SQL next→cause、同型混合cycle/重複・後からfatal | C22–26元fatalと列挙edge、34帰還、36–41fatal/列挙edge。同一の独立1437期待をWeb local portへ対応付け、API結果をWeb成功へ転用しない | D1/D2。実Web/readiness/closeはD3 |
| PT-WEB-STARTUP-GRAPH330002 | SS312:13/SS342:11、1437:10 | W7–34。direct/cause/suppressed/linked、空JMS/SQL/Throwable/null、component=PUBLIC | C51–65元Error順位、66–73非fatal/null・PUBLIC is unavailable/cause null/suppressed0。componentの任意値/null許容契約はこのassertionから決めない | D1/D2。component caller制約の証拠/実起動はD3 |
| PT-WEB-STARTUP-GRAPH330003 | SS312:15/SS354:41、1437:11 | W38–47。same/distinct object、disabled Runtime/Error、primary/secondary graph | C80–83同一/別object、87–107disabled順位/普通帰還、108–111null、helper114–127。APIと独立したWeb assertionである | D1/D2。全caller finally/TWR・完了解放はD3 |

## method/分岐ごとの静的判断と限界

| 観点 | コード/要求から確認した記述 | 既9Test設計で確認する範囲/未確認 |
|---|---|---|
| constructor/null | A11–13は引数なし固定literal。W7–8は渡されたcomponent＋literal。SS312:13のprovider graphを新catalogへ保持しない契約 | T003/B002/C002は初期message/cause/suppressed。Web componentはPUBLICだけ、null/空/任意provider文言の契約・caller制約は対象資料だけでは未確定。未承認のruntime null拒否や一般redactionを推測追加しない |
| preserveFatal null/direct Error | A17–18/W13–14でnull検査→直接Error同一object throw | 329002/003・330002のassertThrows/assertSameが対応、動的帰還/実例外は未確認。NPEをcatchして正常化するコードではない |
| cause/suppressed/JMSlinked/SQLnext | A27–37/W23–32の各nodeでcause→suppressed列→linked→nextを末尾enqueue | 空/非空・SQL/JMS/non-SQLを既fixtureが持つ。JMS linked getter自体の例外/任意custom Throwable getter等の挙動は要求へ推定追加しない |
| FIFOと優先 | pending.add末尾、remove先頭。直接Errorは最初のguard、他Errorはqueueから取り出された順。SS/1437はfinite graphとFIFOを記載 | BFSの深さとenqueue順が作用する。causeの下の全階層を調べ終えてからsuppressedへ進むDFSではない。329002/330002のcause優先は既fixture内の順位であり、全階層でcause優先という新仕様を作らない。1974:7の矢印はこの局所enqueue順として限定して読む |
| identity visited/finite cycle | A20–26/W16–22はIdentityHashMap-backed set、既訪問をcontinue | 329001/330001にmixed cycle/self-next/aliasがある。現fixtureは独自equals overrideを持たないためidentityとequalsの相違そのものの動的識別は未証明。有限・安定graphの静的構造を、実liveness/任意巨大graphの保証へ拡張しない |
| 元object非破壊 | preserveFatal自体はgetterと内部queue/setを使用しgraphのsetter/attachmentを呼ばない | 001は列挙edgeをassertSame/ArrayEquals。graph内の全edge/propertyを網羅的にassertしてはいない。attachSecondaryの意図的追記まで「元object不変」と呼ばない |
| same-object attachment | A46/W41はprimary!=secondaryの時だけaddSuppressed | 330003はordinary same-objectでsuppressed0を確認する設計。全primary種別・既suppressed全配置の網羅をこの一例から認定しない |
| distinct attachment | A47/W42はsecondaryをprimaryへ意図的に連結 | 330003は別object一件とidentity配列を確認。通常suppressionが有効な枝では、このmethodは分類せずreturnする。単独で常にfatalをthrowするportではなく、callerの後段分類が別条件 |
| suppression無効/primary優先 | A48–51/W43–45は追記できずsuppressed length0ならprimary graph→secondary graphを分類 | 330003のdisabled Runtime/Error/helperとfirstFatal/secondary fatal/ordinary/nullに対応。一般attachment成功時の全caller選択順・close優先をこのhelperから認定しない |
| 固定catalog/cause非保持 | A constructorは固定文字列、Wはcomponent文字列のみでprovider Throwableをconstructorへ渡さない | 003/002が新objectのcause null/suppressed0をassert。任意componentの機密性、providerからcatalogへの全変換site、後から外部がcauseを設定する可否は別問題 |
| 並行/timeout/全分岐 | Mainのpending/seenは呼出local、Testの@Timeout5秒は設計上の限度 | 9件には並行呼出の明示競合assertionはない。timeout annotationの存在は実時間内帰還/全条件実測の証拠ではない。line/method/class/branch実測値は本レビューで作らずnull |

## 指摘・残存リスク・必要な判断

R-01: 1974の「直接Error→cause→…」を階層全体の絶対優先と読むと、実queueと異なる仕様を捏造する。上表で局所enqueue順と既fixture順位へ限定した。Main/正本SS/元test oracleは変更していない。新たな業務順位の承認要求やバグを、この曖昧な略記だけで起票しない。

R-02: 「全edge/identity/非破壊/全条件」を9Testの存在だけで満たしたとはしない。具体的な列挙edge・assertionはmatrix、identity対equalsの動的識別/全getter・全階層・並行/全caller資源後条件は未証明として残す。実測欠落を新fixtureで探る作業は今回許可されておらず、ケース・ハーネスは作っていない。

R-03: W constructorのcomponent契約はPUBLIC例以外を当資料だけで認定できない。null/任意値の新仕様・security flaw・上位設計誤りとは断定せず、必要なcaller contractの資料確認が許可された後に判断する。既記載要求との確定不一致は本静的範囲で発見していないため、新BUG/QA/SSCを推測起票しない。

R-04: helperのpure port成功はowned close/rollback/commit/ready/実VM/nativeの証拠ではない。SS312:15/21、342:11、354:41/43のcaller後条件は別受入。既1964/53、17/190、工数null、QA051final、Root11、全安全HOLD、source別成果の分離を保持する。

必要な人/平台判断は、未特定拒否の対象範囲とその後の操作許可の判断であり、この文書は解除を求めたり保証したりしない。消失した元通知の再提出・拒否の再現を利用者へ再要求しない。動的再開の具体commandはここに提示せず、元9774/9776計画を許可扱いにしない。将来の受入証拠はD1/D2/D3の正規真正結果・同sourceと個別criteriaの照合であり、静的レビュー完了又は旧source成功を代入しない。

## 別工程への依存・許可・所有の点検

現認定資料内で、残G01のProtocol生成4helper strict適用性、G07歴史未分類4493、G13未確定8/全WBS audit HOLDが別工程候補として明記されている。これらはこの例外分類の動的fixtureに依存せず、公開済み文書の限界/受入依存を整理する読取レビューは区別可能。ただし本限定指令だけで、それらのJava metadata tool/scan/fixture/任意PTの再実行まで許可したとはしない。次は最新477/478と公開checkpointから一つの具体的な文書工程の許可・入力範囲・所有を確認し、独立性が確認できる範囲だけ着手する。対象未特定操作/実Root/native/運用操作を分割又は言換えして進めない。今回の完成はこの静的文書一件・9対応表のみで、PGPT全完了/PMO返答待ちを理由に停止しない。
