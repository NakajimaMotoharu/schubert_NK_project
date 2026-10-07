# 477 GPT-6.1 Sol実行計画・再開判定

2026-10-08 PMO実行・計測改訂。9/30版の開始状態・S0起点・token仮予算・「自動監視なし」は本版で置換する。旧計画はGit履歴へ保全。WBSのscope/費用/受入条件を今回変更しない。プロンプトの作成は製造開始ではなく、利用者が478を実施チャットへ投入して開始する。

## 1. 正本・モデル・運用境界

対象treeは `/home/mini/codex/project1/work/pgpt-foundation`、branchは `dev-foundation`。元PGPT依頼、承認済RD/UI/SS/DIF、[451品質条件](../450_品質/451_Build・静的解析・coverage方針.md)、[473起動主体](473_起動gate主体・共用境界の実装判断.md)を維持する。478が貼付指示、456先頭が実況、460が残件。現在のGit/実環境を正とし、管理HEADや旧成功sourceへ巻き戻さない。

| 担当 | 指定モデル・推論 | 運用 |
|---|---|---|
| PGPT主実行 | GPT-6.1 Sol / high（高） | 実装・独立試験・実接続・品質閉鎖まで一つの親が継続する。設定は利用者が実施チャットで選び、指定と実確認を区別する |
| PMO | GPT-6.1 Sol / ultra（ウルトラ） | 既存毎時診断で進捗・品質・予実を確認。実施モデルを上書きしない |
| 難しい統合判断 | 既承認のGPT-6.1 Sol / ultra限定レビュー | 反復失敗の具体的な未解決反例がある場合に限る。既存権限内で親＋読み取りレビュー1名まで。全履歴fork/追加agent連鎖/定型集計へのモデル投入なし。委任不可なら親が独立資料で点検し継続 |
| 機械集計 | 既存CLI/script | 成功ログ全文をモデルに再読させない |

旧例外のAstra/high交代は具体的反例がSol限定レビュー後も残る場合のみ、同時併走なし。モデル変更を毎時監査が自動実施しない。これは既承認分担の維持で、モデル性能による値引きを見積りへ加えない。

## 2. WBSと費用の比較基点

現行正本は [479](479_詳細WBS・進捗算定規則.md)、481/484、全対象主担当485、現行実績486。旧v1は482/Git65eddc固定。WBS-v2-20261007-PMO／WBS-cost-v2-20261007-PMOを開始基点とする。190元ID、83子、費用leaf252（予備K02を除く実作業251）。281RD・935artifact・24画面・64layoutの割当済みは要件充足の認定ではない。

残費用は低90.90／標準269.80／高642.60 **週次共有枠pp**、確度LOW。100ppは枠1回分で、token数・費用・暦週へ換算しない。旧476の4,250万/9,350万/1億8,700万Nと旧S1の425～850万Nは過去仮説として保全し、現行残費用の予算や停止上限に再利用しない。今回の開始後実測からtoken見積りを較正する。

G13.07の初期trace照合を先行して、要求・対象artifact・TestID・独立oracle・担当WBSを結ぶ。G13.01～.06の領域別照合を対象着手前に行い、不足をWBS/見積りの版変更として保存する。最終G13はrelease差分まで再照合する。G13全完了を通常製造の先行条件にして循環させない。depsは受入終了条件で、早期調査・captureを禁止する条件ではない。

36共有classの製造/共通PT/共通counterは主担当だけ。消費側固有の業務契約/oracleは別途必要。P019-02参照は0費用、単独達成へ加点しない。親子費・共通費を二重加算しない。21宣言interfaceのcounter非適用は理由付きで保持し、契約監査やJava対象の除外へ拡大しない。

92 HOST_COUNTERS_CLOSED／23 HOST_GAPS／7 NON_JAVA／1 REFERENCE_ONLYは技術測定の内訳。旧89→92はscope/主担当/適用性変更であり今回の新成果ではない。個別criteria・同source証跡・終了依存・QA解決までACCEPTEDにしない。工数完成率は未較正null、旧48.3%や試験/行/commit数で工程率を作らない。

## 3. 保存点と最初の実行

以下は **10/7 02:55停止記録の履歴**。VM/processの現在生存や成功を保証しない。

| 区分 | 保存点 |
|---|---|
| Production | a2e98ce9e96c42425921e3686e8ae7a94bff9e6c、PG495、release0.1.0-PG495、schema028 |
| host限定全回帰 | PG495 3411PT/510suite/FES0/静的6module0。global100/正式/native全体未受入 |
| 当source限定VM | PG498 signed typed BOM187/SQL28/history29 readonly検証、pending code-only公開。新親真正DONEではない |
| PG498証跡 | evidence/01_PT/018_NK-OPS-001/evidence/provisional/PG498-pending-readonly-v2/manifest.json、after参照SHA1ef541deba93311f167df38135930dd1a935fddb7cc54d9cf2b02bfb1b77fdc3 |
| 次の未完 | PG499 runtime退役v1は工具pinのGit正規化hashと原byteの不一致でSAVE前拒否。BUG808/YKT577、host28assert是正済み、実VM再試験未実行 |
| 正式 | PT-WEB-20260925-24、source858713c0bf310ae8bf62078b0a1cedbce4e968db、1964PT/53scope |
| 外部保留 | QA051比較範囲/表記だけ。独立Log/replay等は継続可、L01最終PASSにしない |

再開順：fresh枠→Git/既存dirty/最新HEAD→実施側が現在VM・Unit/kernel/process・署名/source/epoch・保全原値を再認証→初期trace/WBS群と計測窓を確定→PG499正規退役の実再試験→別fresh一回用通常resume→当source真正親DONE/owned停止/native→残製造・CHR・coverage・正式gate/引継ぎ。

最初のhost commandは `python3 -B tools/quality/vm/050_s1/pg499_runtime_retirement_test.py`。是正refsを別new-only TOOLS v2/compile-v3/native-v2へ固定し、新M/A/専用DB/十RefでPG499退役・dirsync/reload・全新scope正常を実証する。原runtime pg492-once-resume.confの退役未実行を再確認してから処理する。旧pg499_retirement_native_v1.py/旧PG492 wrappersを直接再実行しない。

退役完了後、別fresh一回用設定→durable一回予約/observer/外部Morning→**元30分の同Root/API所有を保ったWeb/Caddyと真正DONE**→逆順ownedTERM/native同a2へ進む。旧PG493親143/旧native143/UNKNOWNを新成功で正常化しない。新sourceがあれば、当sourceへ正当に再束縛して再検証し、a2へresetしない。

stash7、元Scenario3、Current baseline、旧失敗cohort・private originals/Backup/DBを保全し、未知ownerへの操作や二重起動をしない。正式DIF以外の業務仕様を変えない。QA047原因・対策・再発防止、QA048業務DB正と整合構造、QA049承認事項、QA050の15分周期＋IT/ST性能時に調整という既方針も維持する。

## 4. 実行粒度と品質

未完の新規経路は一つ。その所有・契約に必要な変更群を閉じてから次の依存作業へ進む。G13初期照合、一区切り完了、通常報告、push、限定レビューの終了で停止しない。資料だけで終了せずPG/PT全完了又は停止条件まで自走する。大幅な仕様/工程/モデル/品質変更は利用者判断へ提示し、独立承認済み作業を継続する。

451のJava四counter各100%、適用JS100%、静的0、独立oracle、境界/null/異常/並行/再送、BUG修正前再現/YKT、Current baseline、CHR/DIF、秘密/trace、正式同一source/run/scopeは不変更。Production自身から期待値を作らず、人工呼出し・対象除外・成功読み替えで100%にしない。Backup所定FAILED/SKIPPED起動継続は正規分岐として保ち、未実行をその結果へ置換しない。Backup成功を新絶対条件にしない。

開発中は変更moduleと影響suite、全回帰は契約変更群/横断変更/受入gateで必要な範囲を選ぶ。triggerと未実行範囲を記録し、同source成功全回帰を根拠なく反復しない。正式runはsource/試験/設定/toolsを固定し、失敗・skip/flaky/not-run・未認定stash・別sourceの成功を混ぜない。

WBS更新前後は `python3 -B tools/quality/wbs_progress_audit.py`。`--baseline-v1` は旧比較保全の必要時/最終時に実施。管理検査をProduction PTへ加算しない。受入/見積り/scope変更は481/484/485/486に版・根拠・前後差を残す。確定RD/UI/SSはAGENTS.mdに従い当作業中に設計だけmainへ反映し、PGPT全完了まで待たない。

## 5. 実施側計測とPMO毎時監査

[487計測規約](487_WBS実行計測規約.json)を適用する。実施側だけが `/home/mini/codex/project1/work/PMO/pgpt-execution-metrics/events.jsonl` を追記し、PMOは読み取りだけ。開始/作業群開始/意味ある実装・試験区切り/失敗・再試行/受入/停止/全完了で1event、長時間job中は約1時間ごとに既知状態のみcheckpoint。監査専用 `/home/mini/codex/project1/work/PMO/hourly-monitor` はPMOのみが更新する。監査用返信依頼・PMO返答待ちは作らない。

着手前のleaf単位低/標準/高見積りを固定し、群/source/run・達成criteria・未達・再開・scope増減・実経路/coverage/正式差・実時間・retry原因・次command・残見積りを保存する。元baselineの残269.80ppを実績の発生とともに消してしまわず、初期予算/累積実消費/現行残予算/完了時見込みを分ける。実時間はmodel稼働と外部job待ちを区別し、時間経過だけで停滞にしない。

usageは取得時刻・limitID・窓長・reset・used/remainingの前後。reset跨ぎ、並走他chat/PMO/レビューが不明なら個別actualSpentPp=null、共有観測差のまま保存。単独WBSと他費0が証明された時だけ481/484のactualObservationsへ配賦する。親子/成果数割/同観測の二重配賦は禁止。

**実token計測**はusage数値だけを取得する既存機能、又は本版 `tools/quality/pmo_usage_increment.py` の増分収集を使用する。初回は末尾cursorを作り、全過去会話・内部推論・成功rawログを再読しない。数値usageをresponse_id単位に重複除去し、圧縮を含むresponse記録も対象にする。N=input−cached_input+output、T=input+output、cachedは入力内数/reasoningは出力内数。親・許可されたレビュー・PMOを別々に数え、未発見子やschema不明/欠測/flush遅延は欠測範囲を残す。token_count累計差やquota割合から実N/Tを捏造しない。実数を得られない場合はnull＋取得不能理由、監査/製造をその理由だけで停止しない。計測開始前の今turn分は未捕捉と記す。

標準枠超過又は同reset追加5ppの観測ごとに予実/原因/次受入証拠を自己点検する。混合観測の超過は診断用で、PGPT専有予算超過と断定しない。同原因反復や約20ppで実経路証拠が増えない場合は対象限定の接続/所有/oracle点検を行い、必要な差分と次観測を具体化する。数値到達だけで停止/合格/品質緩和はしない。

既存 `schubert-nk-pmo` を約毎時で利用し、wait_threads増分、Git、最新456、変更WBS/487eventの小範囲を確認する。PMOは実施branch/台帳/VM/jobへ介入せず、根拠ある既方針内の軽微是正だけ同実施チャットへ1回送る。親が対応中の事項を重複送信しない。PMO/他chatを含む共有観測とPGPT実tokenを分け、通知は意味ある進展/是正/失敗/判断/停止だけ。

実行停止・全完了時は、PMOが監査領域へrun-summaryを保存する。作業群別の凍結見積り/実数/欠測・初回合格/再試行・原因・scope改訂・残見積り・品質/実経路の達成を集計し、WBS見直しの候補を提示する。枠停止はPGPT全完了と読み替えず未完を繰越す。今の計画にない大幅な見積り/モデル変更は自動で確定しない。

## 6. 停止・保全・復帰

実施側は開始と意味ある区切りでfresh枠を照会する。週次又は該当短期残10%以下で新規実装を止め、必要検証・証跡/差分/計測/次commandを保全し、5%付近までに停止する。保全余力不足なら早めに新着手を控える。取得不能時は現在UI値でも確認可、両方不明なら新規実装を始めない。自動reset券消費・追加課金・枠回復による無指示再開はしない。

毎時監査自身は残10%以下又は枠取得不能で新監査/是正を始めず、最小停止記録を残し既存schedule/prompt/target等を維持してPAUSED、結果確認する。PGPTを強制停止しない。PG/PT全完了又は利用者による実施停止でも監査をPAUSEDにする。単なるidle/turn完了だけでPGPT全完了と判断しない。

その他の実施停止はPG/PT全完了、利用者停止、実環境継続不能、不可欠な外部入力待ちで独立作業も尽きた場合。中断前に456先頭/460とeventへHEAD/dirty・source/run・所有/job/安全な証跡参照・枠・最後の計測cursor・未認定・次commandを永続保存する。復帰は478 Bで同じ現在地から継続し、既実行の起動/配備/退役/試験を二重発行しない。
