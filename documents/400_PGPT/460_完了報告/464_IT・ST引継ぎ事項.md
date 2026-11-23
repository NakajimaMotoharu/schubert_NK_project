# IT・ST引継ぎ事項

## 2026-11-23 22:34 JST V031・実DBと配布引継ぎの追補

SSC-479を設計正本main e8cd2907で確認。V031 checksum 1880247817は独立計算と固定Flyway資源の一致値。権限と所有が成立した実DBで、新規／V030更新を分けて適用し、V031履歴・対象owner既定ACL・旧個別ACL同値・再試行0を観測する。旧SQLとCurrent baselineを保持し、正規release履歴を実際の候補で照合する。QA-061の配布条件・担当は未決。IT/ST開始の判定は未実施。 [現判定と根拠](../../../evidence/01_PT/018_NK-OPS-001/evidence/PG43674-current-stage-and-handoff-v1/manifest.json)

## 2026-11-23 21:01 JST C08の配布・復旧引継ぎ照合

承認済みSS353のRB-001～010を、現候補で渡せる10件の技術区分と、実Linuxで取得する証拠に対応付けた。担当欄は設計上の役割で、個人の割当や受領は未確定。実効Unit・実DB/JMS・FileStore・native・Browser、同候補の署名BOMと配布条件・承認担当、切戻し判定が残る。QA-061の配布条件と担当は未決。実環境の取得・受領済み0、IT/ST開始判定未到達。 [C08の十項目と原証跡](../../../evidence/01_PT/018_NK-OPS-001/evidence/PG43618-c08-itst-handoff-static-prerequisites/manifest.json)

## 2026-11-23 18:09 JST PG43500 外部依存POMの親宣言

取得元POMに直接欄がない17座標は、同じ保全cacheの親POMを追い、17件すべての最も近い宣言箇所を固定した。現四製品の36件は直接19／親宣言17の局所根拠を持つ。P019-02は共通成果参照で追加費0。配布条件・承認担当、署名付き全六の実配布クラスパスと実際の判定は未成立。 [PG43500](../../../evidence/01_PT/018_NK-OPS-001/evidence/PG43500-current-retained-parent-license-declarations-v1/manifest.json)

## 2026-11-23 四正規製品の配布依存メタデータ

外部36座標のcacheを同一SHAで照合。取得元POMでライセンスの直接欄19、直接欄のないPOM17。18 archiveの通知・ライセンス名候補は旧記録のpath/hashを同一バイトから参照した。製品配布条件・承認担当はQA-061の回答どおり未決。署名付き全六製品と実配布クラスパスを照合してから判定する。 [PG43498](../../../evidence/01_PT/018_NK-OPS-001/evidence/PG43498-current-four-external-license-inputs-v1/manifest.json)

## 2026-11-23 現四モデルの外部archiveの技術証拠

四正規製品の既存有効モデルに外部36座標があり、同じ保全cache内の36実ファイルのSHA-256を元証跡と照合した。外部compile 40・runtime 6 edge。保全cache側の証拠であり、署名付き実配布クラスパスと配布条件・承認担当は未決。 [PG43428](../../../evidence/01_PT/018_NK-OPS-001/evidence/PG43428-four-model-cache-byte-provenance-v1/manifest.json)

## 2026-11-23 15:23 JST 正規四製品のMaven依存とQA-061

Protocol／Storage／Bootstrap／Batchの実効compile/runtimeモデルを現埋込POMと照合。外部36座標に該当する過去宣言36、通知名候補18、該当名観測なし18。署名付き同候補、正規API／Web、配布条件・承認担当、実配布class pathの照合を次の判定に要する。 [PG43404](../../../evidence/01_PT/018_NK-OPS-001/evidence/PG43404-four-regular-runtime-tree-offline-v2/manifest.json) [PG43406](../../../evidence/01_PT/018_NK-OPS-001/evidence/PG43406-current-four-models-labeled-license-metadata-v1/manifest.json)

## 2026-11-23 短期WBSの終了依存とLinux側の引渡し

短期66行のうち、着手条件欄にF02・F03の正式終了を明記した行は延べではなく12行。F02は12行、F03は12行で、両方を要するのは12行。担当へ渡す局所証拠の作成は、各作業の実施許可と入力が揃う範囲で継続する。正式受入16/190、開始17件に対して純減1件、指定0/12、中核0/5。12月6日18:00 JSTの元基準27件へ現時点から11件。原計画・改訂計画・共有消費の管理は既記録を参照する。

| 担当 | 次に必要な証拠 |
| --- | --- |
| F02 ビルド・アーキテクチャ | QA-056四型の扱い、現API/Webの正規JAR、Storage旧JDBC辺を置き換える責務と残呼出の適用、現六製品の依存監査。監査工具の終了不備は局所是正済み。 |
| F03 品質 | 保留32試験とRoot11の処置、当六製品の同一source/runで静的・全PT・四指標・451、正式担当判定。試験書式は個別根拠が確認できた359/1,135を維持。 |
| C02 Linux運用 | 同bootとUnit Invocationで所有、DB/JMS/実効Unit、API/Web/Caddyの実起動・真正終端と逆順停止を証明。 |
| F04 環境・実証 | harukaの現所有・許可・資源と実FileStore、実Browser／実NK比較の同候補の証拠。利用解除済みaruは依存から除く。 |

11月25日23:29 JSTの四担当の受領と、12月2日23:29 JSTのF02/F03正式判定は未確認。配布条件と担当はQA-061の回答に基づき未決。[短期依存の照合証跡](../../../evidence/01_PT/018_NK-OPS-001/evidence/PG43352-g12-short-wbs-exit-dependency-join-v1/manifest.json)

## 2026-11-23 現候補の差分とLinux受領条件

製品Core `87927ea17c1c8dbef528bc0c6882c24b1fe7c871`。正式認定はPT-WEB-20260925-24の1964試験／53領域、有効受入16/190、指定0/12。局所試験と工具試験は別集計。IT/ST開始には同じ製品候補のPG/PT正式終端、署名付きBOM、環境・所有、切戻しの承認が必要。引継ぎ先の受領と開始日は未確定。

| 担当範囲 | 現候補で引き継げる追加証拠 | 引き継ぎ先に必要な結果 |
| --- | --- | --- |
| ビルド・品質 | Java宣言1033、正規4製品／1116物理。旧SSC447の152件は元source別。Schema履歴の個別methodと参照・検査DAOの局所計測を現候補へ対応。 | QA-056の適用判断、API/Web正規JAR、Storageの現JDBC境界と保留32入力／Root11の判断、六製品同一source・runの451。 [六製品の差分](../../../evidence/01_PT/018_NK-OPS-001/evidence/PG43256-f03-six-product-local-proof-delta-v1/manifest.json) |
| Linux・運用 | 既Unit宣言14とtimeout 4件は現候補に一致。05:00 JSTのtimer宣言確認。局所JDK/Javac25.0.4と既Maven3.9.12実体を照合。 | 固定maintenance.service、本番適用確認、同bootのUnit所有、API/Web/Caddyの真正起動と逆順停止。旧配備状態・接続観測から現候補を認定しない。 [PG43182](../../../evidence/01_PT/018_NK-OPS-001/evidence/PG43182-c02-current-declarations-and-missing-effective-state-v1/manifest.json) [PG43194](../../../evidence/01_PT/018_NK-OPS-001/evidence/PG43194-f04-local-tooling-current-handoff-v1/manifest.json) |
| DB・メッセージ | 参照DAO10件と検査summary DAO13件が別々の単一実行で成功し、各対象の生四指標100%。清掃通常読取5件、JMS Guard／Writer14件の局所証跡を保持。 | 承認済みLinux環境で借用接続・JMS実効設定、原本/Backup保持、再送時の重複防止と処理後条件。実DB、実Broker、実移行と前節の性能試験は対象ごとの条件を満たして着手する。 [参照DAO](../../../evidence/01_PT/018_NK-OPS-001/evidence/PG43238-p00403-reference-ten-single-exec-v1/manifest.json) [検査summary DAO](../../../evidence/01_PT/018_NK-OPS-001/evidence/PG43254-p00402-inspection-summary-corrected13-v1/manifest.json) [JMS局所](../../../evidence/01_PT/018_NK-OPS-001/evidence/PG43204-p00503-guard-dlq-record-observations-v3/manifest.json) |
| 実互換・native | 証跡工具は出力途中失敗を非zero扱いに修正。公開差分59commitの秘密スキャン検出0。 | 同候補の実NK CHR、元Current基準保持、当sourceのCRC/session/owner、実Browser、実効nativeと451の同じ証跡束。 [PG43210](../../../evidence/01_PT/018_NK-OPS-001/evidence/PG43210-p0180803-coverage-output-terminal-v1/manifest.json) [PG43214](../../../evidence/01_PT/018_NK-OPS-001/evidence/PG43214-g07-since-43136-public-delta-v1/manifest.json) |
| 配布 | 正規4 JARの自身Maven座標を確認。4 JARのルートとMETA-INFに対象名の通知エントリ0。過去の6 SBOMには外部69座標の宣言記録あり。 | 製品配布条件、外部依存ライセンス判定基準と承認担当、同候補の最終収録範囲と必要な通知、署名。QA-061の回答を受領し、条件と担当は未決。 [包装構成](../../../evidence/01_PT/018_NK-OPS-001/evidence/PG43192-p01802-candidate-jar-composition-v1/manifest.json) [宣言の照合](../../../evidence/01_PT/018_NK-OPS-001/evidence/PG43228-p01802-retained-license-declarations-v1/manifest.json) [通知の収録状況](../../../evidence/01_PT/018_NK-OPS-001/evidence/PG43230-p01802-four-regular-notice-entries-v1/manifest.json) |

配布資料の追補。現行POMの外部直接compile/runtimeは41宣言、20座標。保存済み宣言メタデータに全41宣言が同製品・同版で対応する。test/provided 24宣言は別計上。現JARの推移依存と最終通知、配布条件・担当は引き続き判定待ち。[現POM照合](../../../evidence/01_PT/018_NK-OPS-001/evidence/PG43284-p01802-direct-release-declaration-lineage-v1/manifest.json)。

過去候補、再送・性能の合格条件、移行と復元の未実測値は下段に保全する。

## 2026-11-23 現候補の引継ぎ条件と再送の実測区分

現製品候補は `7698011f52d6cc5f94c76413b6ab36971783b9c9`。正規のProtocol・Storage・Bootstrap・Batchの4製品を照合し、API・Webの正規JARとStorageのJDBC責務、全6製品の同一source/runでの451、担当の正式受領が残る。過去の認定1964試験／53領域を維持し、現候補の局所結果をその件数に加算しない。PG/PTの受入、実NK互換、nativeと実起動の残条件は456・460で管理する。この候補に対するIT/STの開始日は未確定。[現F03と六製品表](../../../evidence/01_PT/018_NK-OPS-001/evidence/PG43000-f03-current-batch-window-scope-v1/manifest.json)

| 測る経路 | 承認済みの期待と後続で提出する証拠 |
| --- | --- |
| Logout失効確認 | 初期5秒・30秒・5分、その後15分。通常負荷のみの計測と、同じ負荷に再試行を重ねた計測を比較する。due集中、障害復帰、複数worker、残件100・1,000・10,000の各試験点について、失効確定までの所要時間、待機残件、重複と削除結果を記録する。検証済み0000・0200だけを自動削除の根拠とし、未確認0102等の保持も確認する。間隔を変更する場合はIT/STの実測を根拠に承認手続きと同条件の再試験を行う。 |
| 業務Outbox送信 | 1秒・5秒・30秒・1分・以降5分cap。再送のjitterは±10%、最初の受付確認sendには適用しない。ローカルの固定時刻試験は成立。Linux側はclaim・JMS commit・SENT更新の障害境界、同Message ID再送、重複排除とDB/JMS後条件を同source/runで採取する。 |
| Broker受信再配送 | 初回受信後の1秒・5秒・25秒。実効Address設定、配送回数、恒久失敗と最終失敗のDLQ・job終端、個別replayを照合する。 |

正式実測ではrelease・署名付きBOM・当bootと実効Unit・担当と権限・run開始終端を固定し、操作前後のGuard、DB・原本とBackupの観測を同一環境で結ぶ。既HOLDの試行や実環境操作は発行許可といずれの開始条件も確認してから扱う。QA-061は配布条件と判定担当が未決。配布の承認基準、担当、同成果物の構成表・署名を受領するまで配布判定は保留。[SS362](../../300_SS/360_引継ぎ・監査/362_PG・PT・IT工程引継ぎ事項.md)・[QA-061記録](../../../evidence/01_PT/018_NK-OPS-001/5708_QA061回答と配布判定残条件.md)


## 2026-11-23 Linux側への引継ぎ候補と開始条件

正式認定はPT-WEB-20260925-24の1964試験／53領域。元WBSの有効受入は16/190、短期指定0/12、工数完成率は未較正。現Java Coreは `e8368d22c4da2ec841f008df793594d3be9066af`。正式開始判定にはPG/PTの同一sourceの終端、署名付きBOM、承認された対象環境・担当、変更と切戻しの記録を揃える。[SS362](../../300_SS/360_引継ぎ・監査/362_PG・PT・IT工程引継ぎ事項.md)

| 担当 | 現候補で引き継げる証拠 | 開始・完了までに取得する証拠 |
| --- | --- | --- |
| ビルド・品質 | Protocolの実offline CIはJDK25.0.4／Maven3.9.12、JUnit171／39、標準JaCoCo四指標100%、SpotBugs0、現通常JAR。旧正式53領域は公開履歴から再照合。 | StorageのJDBC責務、APIとWebの正規JAR、現sourceの全製品・全必須scope、保留32入力とRoot11、現Batch完全目録、451正式判定。 |
| Linux・運用 | 下段の05:00 JSTタイマー、外部監視へ渡す判定値、同runの開始／完了marker契約。 | 承認済みLinuxの現在boot、rendered Unit・有効設定・所有者、普通API/Web/Caddyの起動と順序、同一環境での保守・停止・再起動・監視の真正後条件。 |
| DB・移行・復元 | 既定の変更管理、固定DDLと独立期待値、比較用Current baseline。 | 同source・同環境でのJDK/DB/Artemisの正規バージョン、移行全件（設計基準59,627ファイル・19.24 GB）の件数／hash／時間、DB query planと物理サイズ、Backup 7世代・80 GBとRTO 24時間の復元時系列。実原本・Backupの使用と責任者を先に確認する。 |
| 性能・互換 | QA-050の承認済み初期backoffと、その後15分間隔。現起動・Broker・Webの実測は未受入。 | Linux上のWeb/API JVM・DB pool/SQL・Artemis journal/paging容量、再送と重複防止の実測、実CHR-A01/L01と現source native。性能に問題が確認された場合は承認手順を通して間隔を変更し、再試験する。 |
| 配布・ライセンス | QA-061は回答受領、配布条件と判定担当は未決。候補構成表・配布元のhash・依存検査の局所結果を保持。 | 配布条件、依存ライセンスの受入基準と判定担当、同候補の実配布成果物・構成表・署名・承認を突合する。 |

PG/PT側の残件は451と456で追跡する。Linux側は実測範囲・source/run・日時・OS/JDK/ミドルウェア・対象識別・次操作の承認を分けて受領する。各担当の正式受領、同一sourceの実インフラ・性能試験、IT/ST開始判定はいずれも未到達。

[Protocol実CI](../../../evidence/01_PT/018_NK-OPS-001/5714_ProtocolローカルCI実行_仕様と結果.md)・[旧認定の原証跡](../../../evidence/01_PT/018_NK-OPS-001/evidence/PG42746-g08-certified-historical-53-v1/manifest.json)・[配布判定](../../../evidence/01_PT/018_NK-OPS-001/5708_QA061回答と配布判定残条件.md)

## 2026-11-22 日次保守の監視判定と運用検収

現Java候補 8c99fbd2112183808d8d973bce7b3a9b3c1cef13。Maven包装済みのBatch JARから追加された3物理を照合し、同候補の期限判定8件と、JAR由来の通常CLI入口4例を確認した。後者は外部監視へ接続せず、合成された観測値を入力した。timerの設定候補と構文証拠は下段を参照する。

| 受入条件 | 担当と取得する証拠 |
|---|---|
| 同runの開始・完了、旧bootと新bootの差、期限 | PG/PT担当が現候補の開始と完了markerの採取契約を確定。運用・IT担当が承認済みLinuxで相関時刻、同一run、新しいbootと対象機の同一性を確認する。 |
| 60分以内の正常復旧と60分未更新 | IT/ST担当が、対象機の外側の監視から二経路を独立に観測。正常側の完了と期限超過側のcritical通知・通知時刻を各々保存する。 |
| 権限、実効Unit、停止と復旧後条件 | 環境担当が同一source/BOMの実効設定、起動主体、親子Invocation、同runでの排他と停止後条件を採取する。設備と実行権限が確定してから実施する。 |

証跡 evidence/01_PT/018_NK-OPS-001/evidence/PG42412-g1306-watch-packaged-cli-proof-v1/manifest.json SHA256 9a712c899a20404d845c37ebbe1fee669c2221f8cf6c858823a65506390df990。PG42418で同候補の包装、CLI、設定、局所PTを接続。正式認定1964試験／53scope、元WBS 16/190。PG/PTの実サービス・監視接続と全体451は引き続き検証する。


## 2026-11-22 JST 日次タイマーの現候補とLinuxへ渡す条件

現設定候補は 3b0139d02a7a87042139718b9ffbe2f795b1837b。05:00 JST、時刻精度1分、ランダム遅延0、過去予定の追い付き実行なし。PG42370 T03の設定確認とPG42388 T04のsystemd構文確認が成立。T01/T02の旧時刻証拠は元sourceを保持。構文検査では試験専用サービスを使用し、参照ファイルの欠落は構文終了とは別に検査する。

- PG/PTでは、固定本番サービスの製造、同一所有者の排他、停止順・真正終端、更新と再起動の安全判定を閉じる。実サービスの受入後にタイマーを実配備する。
- 承認済みLinux環境では、同source／BOMのrendered timer/serviceを両方照合する。実効次回時刻、制限、予定とmanual再実行の排他、停止・復旧前後の同run／異bootを採取する。
- 外部監視で保守開始と同runのreboot完了markerを照合する。60分の未更新criticalと、時限内復旧の対照を別々に確認する。監視接続・配備が未認証なら保留を維持する。

証跡 evidence/01_PT/018_NK-OPS-001/evidence/PG42392-g12-timer-updated-linux-handoff-v1/manifest.json SHA256 879efd8a4240ba6e06e4a9011fb796043564d79ddefe142c2e525efaae2e90be。正式1964試験／53スコープ、WBS16/190。IT/STは後続工程。


## 2026-11-22 JST 日次保守timerのPG/PT引渡し・工程継続中

最新の正式認定は1964試験／53scope、WBS正式16/190。設定候補 27152c62e0b39a9fafa9aa2fd4576a9efb905da9 の05:00 JST timerはPG42306のoffline二条件で成立。既存batch.ymlの時刻・zoneと一致。後続の着手には承認済みserviceの製造、M排他、60分期限、固定stop順、更新・reboot安全の独立PT、環境所有と当sourceのrendered Unit/BOMが必要。実Unit・監視marker・再起動・保持条件の検証は後続の承認済みLinux環境へ引き継ぐ。工数率は未較正。

証跡 evidence/01_PT/018_NK-OPS-001/evidence/PG42306-g1306-maintenance-timer-offline-v1/manifest.json SHA256 fcaed552f0f726ca27ce485b9a7c6c57bff013234a84215926e32ae4bffe4126。


<!-- PGPT-CURRENT-20261108-HANDOFF-BEGIN -->
## 2026-11-08T23:51:30.065774+09:00 最新技術成果（PG/PT継続中・工程未完了）

この追記を下段の過去報告に優先する。正式認定は **PT-WEB-20260925-24／1964PT／53scope** のまま。歴史WBS17/190と今回新規受入0件を分離し、**工数完成率は未較正null**。下段の旧割合・未回答QA・実行中job・VM/PID/boot記録は現在値に読み替えない。

| 区分 | 当時点の確認済み事実 | 証跡 |
|---|---|---|
| Production Main | `7aed8eace7c844c2f79f2e39db766faf914890d5`。配置・実起動の認定ではない | normal PG22084/PG22086、各当run source照合 |
| 匿名Log追加 | source `8a027340a317584d5c80fb071e92da368439d07f`、既存15＋新規1＝16件成功。新規はPT-PRO-QA054-013一件だけ | PG24544／24546 `b8f150d8`、Program002仕様090/結果091 |
| protocol全体 | Test source `fa7ca8df24fbb4acea1b12b32f8f86aa07438b80`、24fixture119件一回OS0/FESaborted0。実line3478/method742/class159/branch1014、全miss0・module四counter100 | PG24582／24584 `e154d86f`＋必須母数補足PG24594 `9448c8cf`、Program002仕様092/結果093 |
| 母数と限界 | 入力176＝XML/classinfo169＋注釈7、169＝実測159＋interface6＋標準compiler filter4。raw24584の誤命名field169はXMLentryであり実測class159は24594へ訂正。自然branch0の118SourceはN-A/null、全Source非空四100や全451へ換算しない | 24594現byte/CRC/公式filter、手動除外0、旧exec合成0 |
| distinct追加試験 | 累計519＝Java415＋HTML97＋CSS7。119の再資格や上記16を再加算しない。候補114/pending12/旧whole93は暫定 | 4464/4466/4468/4470、456/460の保存点 |
| G07原検出 | 原4493中、分類1213／未分類3280、別container限界22、actualSecretCount=null。新16＋新17は元座標非重複、後者は既SDK証拠を再利用しartifact IO0 | PG24604 `c6dcdaef`／24614 `2519676a`、018仕様3884/3886・結果3885/3887 |
| QA-055 | 回答「現行の固定文を維持する」。Login画面は固定15分文、実待ち秒はHTTP Retry-After。設計main42450b5/PR207へ反映済みで再確認不要 | 911/UIC012/SSC338、局所DOM/header証跡21044/21064と後続元28再資格24414は別run |

**残るPG/PT受入条件**：同source全scopeの451/独立oracle・trace・秘密scan、未解決障害/横展開、実NK CHR、当source native・普通起動/owned停止と独立post、必要PR/merge・全成果保存。上記局所成功を全体受入やIT/ST合格へ加算しない。QA051 final、実VM/Root/cohort/DB/Backup/鍵/native・拒否対象未特定・held四等の既HOLDを維持する。外部job/VMの現在状態は未認証であり、host Unit119の終了0と混同しない。

**Linux server引継ぎ前提**：PG/PT残件をIT/STへ転嫁せず、許可と所有が成立してから当boot/source/BOM/DB/原本Backup/Unit/actor/clientを再認証する。旧PID/permit/旧runを再使用・そのまま復元せず、不明な操作やRoot/配備/停止を再発行しない。IT/ST性能・運用の合格は後続の別工程で実証する。通常の報告・commit・本追記の作成では自走を停止せず、fresh残10%以下/取得不能等の既定停止条件に従う。
<!-- PGPT-CURRENT-20261108-HANDOFF-END -->


2026-10-22追記：SSC333/334/1470 ordinary consumer/broker/parentの終端graph・close順/成功phase・copy wipeは当source限定host127で確認。実UNKNOWN非帰還を解除・実close成功へ変換する変更はない。実native/CHR・global四100・正式と1471全体は当時未受入で、PG/PT残件を後続IT/STへ転嫁しない。署名済み・配備済み・旧boot/native成功を新sourceの所有/資格に読み替えず、実操作のHOLDは478 Dに従う。IT/ST合格宣言0。

## 2026-10-09 当source普通親の実測引継ぎ（PG/PT限定・IT/ST未実施）

現正式はPT-WEB-20260925-24/1964PT/53scopeのまま。新candidate1ec19782a/PG715/schema028はhost3502PT517suite/static6zero、当ordinary55ac sameRootAPI-Web-Caddy/実CurrentA01/真正PID1-RootDONE/ownedstop/全24資源0/八nativeを限定検証済みだが、全四coverage100/全CHR/正式工程は未完了。下段9/20以前の正式・割合は履歴で現在率に使わない。

PG725 original1800sで1794.547089s（余裕5.452911s）、旧PG693 source9bd1752.251786s（別sourceで比較性能認定0）。PG734の一回owned診断ではpermit発行→保持Backup/DB→RootUnit再検証中。Linux serverで同一source・同所有契約/元budgetを保持して起動所要、CPU/DB/Unit・artifact確認の内訳、負荷変動、失敗後逆順停止/復旧、長期運用を測定する。PG/PTだけで性能/ST合格やbudget緩和を宣言しない。今回VMの単発値をp95/RTOへ換算しない。

2026-09-20 最新確定: 正式PT-WEB-20260920-27/source3b980d71f5573342b7c787ad6eed53db6d8c2940、10:14:36～10:27:24 JST/Maven12:47/exit0、全1719PT（Protocol80/Storage82/API689/Web460/Batch367/CHR41）、failed/error/skipped0。6Java全line/method/class/branch100%、Production5 NullAway/Enforcer/Spotless/SpotBugs未解決0、固定path3method限定review継続・coverage除外追加なし、CHR SpotBugs未設定。JS1file全line/function/branch100%、18collector/41scope整合・81負canary成功。DB29/266＋Batch25/281＋OPS17/142＋QST2/16＋ASY1/5＋Web25/219＝99部分成果929PT（全1719の内数）、今回再開比+304PT/+34部分成果。PG215 Log画面状態8PT・PG216実template8PTを限定認定、BUG226/YKT182完了。LogのBrowser入力検査/ADMIN HTTPは未実装。BUG195/206/YKT154/162/SSC063、実archive/親/質問受付全体/残Web・本文controller-file/readiness/Logout/QA045/実NKgateは未完了。固定加重40.85～52.35%（中心46.6%≒47%、約41～52%）を維持。残量9%で利用者指定の停止、元dev-web3file保全、PGPT/IT/ST未完了。以下は履歴。

過去記録（正式12、当時の件数比は現在の加重進捗に使用しない）: 最新確定: 正式PT-WEB-20260909-12、source 970681dfb6e2a0ba021c71402cdc5b69fb950b0d、dev-web、2026-09-09 03:27:49～03:32:41 JST。全790件（Protocol80/Storage34/API394/Web241/CHR41）、failed/error/skipped0、5対象moduleのline/method/class/branch全100%、NullAway/Enforcer/format PASS、SpotBugs0。Web165件、Admin73、Inbox11+3+4、Media61、Scenario155/Auth91等は重複する内数。API0102のlocal session破棄/HTTP終端/全result分類8件を追加PASS、DB削除前・commit故障/実HTTP/100並行/新Login非削除を確認、SSC-048完了、7collector収集成功。CHR41はrunner単体試験であり実NK互換gateではない。Logout revoke queue・本番logger固定/残画面/全layout登録/起動/実NK CHR、QA-045承認依存は継続。確定Program5/20=25%（件数比、工数換算なし）、再走待ち1件（RERUN-001/SSC-045、455のLogout期限設計）。PG-D-118のScenario6電文clientとPT166～173を先行仕様化し、画面接続へ継続する。以下は履歴。

過去記録（正式ADM04）: 最新確定: 正式PT-ADM-20260908-04、source 1f1d321ad40bd7ba5f8461e5954e94e7ac6142d3、dev-admin、2026-09-08 15:59:29～16:03:00 JST。全571件（Protocol80/Storage34/API340/Web76/CHR41）、failed/error/skipped0、5対象moduleのline/method/class/branch全100%、NullAway/Enforcer/format PASS、SpotBugs0。Admin23、Media61、Scenario151/Auth91等は重複する内数。User作成/状態/role/password/unlock、実PG監査・全session失効・故障rollback・独立PBKDF2/USRMUT24・並行raceを追加PASS。BUG-045～047/YKT-040～042は再試験完了。正式03は静的解析失敗で非合格。SSC-031の外側Inbox接続とSSC-032の新規canonical接続、HTTP/起動/実NK CHR、QA-045承認依存は継続。確定Program5/20=25%（件数比、工数換算なし）、明確な行き詰まり0件。以下は履歴。

## 1. 位置づけ

後続Linux serverでのみ確定できるcomponent間、実service、性能・容量・可用性・運用の実測値を引き継ぐ。本工程はIT/ST完了を宣言しない。

未実装のProduction/設定artifact/単体異常系をITへ移してPGPT完了にはしない（460）。実NK比較は本工程の残gateであり、CHR41 runner PTや後続deployed試験で代替しない。

## 2. 初期引継ぎ

| ID | 項目 | PG/PTで保証する範囲 | Linux serverでの確認 | 状態 |
|---|---|---|---|---|
| ITS-H-001 | Caddy/Web/API/Artemis/PostgreSQL接続 | 設定schema、単体契約、sanitized fixture | TLS、systemd順序、実socket/credential/権限 | 引継ぎ予定 |
| ITS-H-002 | Artemis容量・再配送 | Embedded/schema、1/5/25秒、DLQ/Expiry契約 | Journal/paging、disk 90%、restart、実時間 | 引継ぎ予定 |
| ITS-H-003 | PostgreSQL backup/restore | DDL/Flyway、role/grant、command contract | `pg_dump -Fc`/restore、RPO/RTO、専用role | 引継ぎ予定 |
| ITS-H-004 | 性能・大容量file/media | Range/hash/atomic file単体境界 | Master 59,627 file/19,240,707,190 byteで容量・性能 | 引継ぎ予定 |
| ITS-H-005 | Characterization | NK adapterと関連case単体契約 | Deployed NKで24 case、DIF-001～016のみ | 引継ぎ予定 |
| ITS-H-006 | Password照合p95 | pbkdf2-v1/310000/16byte salt/256bitの独立JCA検証、256byte全長差 | 本番CPU/Java25でwarm-up後Login照合p95を測定。SS314の0.5～1.0秒から外れる場合security review。同一IDのparameterを変えない | 引継ぎ予定 |

| ITS-H-007 | Username key拡張migration・切戻し | SSC-014/V007の比較key96byte、表示/audit64byte、旧64byte拒否→DDL拡張、UK/NULL/境界、実Loginの独立PT | 既存schemaからV007へFlyway適用と復旧を実serverで確認。旧codeへ切戻す前にkey64byte超の有無を集計し、存在する場合は切戻し不可として運用判断。値の切捨て/再計算/削除で回避しない。JDK更新でUnicode増幅guardを再実行 | 引継ぎ予定 |

| ITS-H-008 | Transfer filesystem capability | SSC-019の実libc errno/no-replace/保持FD試験、本機Linux amd64合成fixture | 配備OS/CPU/libc、local filesystem/RENAME_NOREPLACE、procfs self FD、directory fsync、所有者0750/0640、systemd hardening下のnative accessとroot差替え拒否、kill/crash耐性。未検証network FS/非対応attributeはreadiness false。Java ATOMIC_MOVEへのfallback禁止 | 引継ぎ予定 |

追加（2026-09-08、SSC-019～022、PT-SCN-20260908-14）: writer/reader/完全metadata scan/診断startup probeの内部部品はlocal ext4＋mini/users合成fixtureで検証済み。Full root実体の非重複、single-instance/exclusive startup、probe→全scan→quota初期化→producer/HTTP開始の結線、Web read-only/API限定writeを実service UID/systemd hardening下で確認する。これらを本PTだけで完了扱いしない。

Probeの公開不確定/変質ready/清掃不能partは起動失敗の証拠として保全し、次回朝清掃・承認済み運用調査へ委ねる。新規dateのchgrp/fsync失敗でempty dateが残る場合がある。既存不一致をアプリ再起動でauto-chmod/chgrpして隠さず、運用者が状況と所有を確認して所定の修復/清掃を行う。業務readyの通常lifecycleは変更しない。Probe失敗後の再起動/運用復旧とsingle-instance競合は後続結線試験に含める。

## 3. 追加引継ぎ（正式47時点）

| ID | PG/PTの確認済み範囲と未完了 | 後続Linux IT/STの確認 |
|---|---|---|
| ITS-H-009 | private Inspectorの専用credential/保持inode/31応答保護・wrapper/oneshot契約を単体確認。親file publish・全結線は未完了 | 実root/UID/ACL/mount、4 previous-key profile、実credential配布、hardeningで同じ拒否条件を確認。秘密実体をGitへ保存しない |
| ITS-H-010 | flock/固定lockfile admission/停止状態読取/run byte/DB handoffを確認。親制御・SSC055永続原本・backup artifactは460残件 | 実停止・子終了・親再取得・reboot/timeout/再attempt・commit不明から復旧、設定公開とbackup restoreの結合を確認。単体の合成root属性を実配備合格にしない |

## 4. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-09-01 | 初期引継ぎ対象を登録。 |
