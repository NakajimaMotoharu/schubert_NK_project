# 477 GPT-6.1 Sol実行計画・再開判定

## 現行：2026-10-20 利用者承認・拒否PTのレビュー／静的チェック代替

利用者はPMOチャットで「拒否部分はPT実施不要（PG実施不要ではない）」と訂正し、その部分をPGの強化レビュー・静的チェックで代替して後続PGPTへ進むことを明示承認した。**PGの実装責務は残す。拒否されたPTの動的実行だけを対象ごとの代替確認へ変更する。** 本節はPT実施方法について旧478、過去のhost限定作業終了条件、「品質条件不変更」の一般記述より優先する。業務仕様・成果の正確な報告・資源操作の安全条件まで免除しない。

### 1. 拒否範囲の特定と保留

- 既存の明示拒否エラー、最後のツール結果、対象source／TestID／command／WBS／依存関係から、拒否PTと関連PGの範囲を照合する。拒否を探る試し実行、再送、言い換え、分割、別モデル・別chat・別経路による再試行はしない。新規に範囲判定用のPTを発行しない。
- 最後の成功コマンドは拒否された操作の証明ではない。今回の停止turn `01a1544d-c46a-7680-b0ce-572a1720aeac` はcybersecurity拒否の対象操作が未特定で、直前のコード読取は終了0である。現時点で特定のPTが拒否されたとは確定しない。
- 特定できない分は `REFUSAL_SCOPE_UNRESOLVED` として関係作業を保留し、既存資料から安全に分離できる独立作業へ進む。判定不能をPT全体・PG全体の免除や実行許可へ拡大しない。
- プラットフォームが拒否した操作自体は保留する。PGや静的チェック自体も拒否された場合は、その処理を別名で継続せず記録する。本承認は安全制限・権限・アクセス条件の解除ではない。

### 2. 代替確認の実施条件

対象を `PT_EXECUTION_EXEMPT_REVIEW_STATIC_PENDING` として登録し、当sourceの既存の承認済み設計・独立期待値とPGを対応付ける。PGが未実装なら許可された実装作業を行い、実装不要とは扱わない。次の両方の証跡が揃うまで代替確認済みにしない。

1. **PG強化レビュー**：要求／SS／TestIDとclass・method・差分を結び、正常・境界・異常・null・例外・並行・再送の適用性、入力／戻り値／状態遷移、依存先、資源の取得・解放、失敗時の後条件と影響範囲を個別点検する。期待値はProduction実装から逆算しない。反証を意識した別パスのレビューを行い、指摘・修正・再確認・残る実測不能事項を記録する。新agentを必須にはせず、許可済みレビュー体制又は親による根拠を分けた再点検を使う。
2. **静的チェック**：許可された既存のformat／compile／型・null／依存・静的解析を対象に適用する。コマンド名ではなく実際の処理で分類し、test／VM接続／サービス・DB操作を暗黙に起動するwrapperは静的チェックとして使わない。拒否対象と同じ操作・セキュリティ検証を静的チェック名義で続行しない。実行できなかったcheckは未実施・理由を残し、終了0へ正常化しない。

保存項目：例外ID、利用者承認日、拒否turn／error digest、拒否操作の識別根拠と確度、source/hash、WBS主担当、要求／criteria／TestID、PG対象、依存範囲、レビュー担当・根拠・指摘と解決、静的check名／command／exit／artifact hash、未実施PT、残存リスク、後続作業の依存判定、次の証跡。秘密情報・私有rawログは保存しない。

### 3. 受入・進捗の表記

- 完了した代替確認は `PT_EXECUTION_EXEMPT_REVIEW_STATIC_COMPLETE` として、利用者承認による**レビュー／静的チェック代替**であることを明示する。未実行PTをPASS・実行済み・native成功・実経路閉鎖へ算入しない。既知の失敗、not-run、UNKNOWNは履歴として保持する。
- 実測coverageがない領域は未測定／未達と記し、100%へ補完・除外して数値を作らない。実行済みPT件数・成功件数・coverageと、代替確認の件数／範囲を別に報告する。
- 対象criteriaのPT実行証拠は本承認の代替確認で充足できる。その他のcriteria・終了依存を照合した上でWBSを閉鎖する場合も、`ACCEPTED_WITH_USER_APPROVED_PT_ALTERNATIVE` の注記・例外参照を付け、無条件の動的検証済みとしない。全体報告には残る実測不足と承認済み例外一覧を必ず含める。
- レビューだけでRoot真正DONE、job終了、process所有、DB不変、lock解放、配備済み、VMの現在状態を証明したことにしない。実操作に必要な安全条件・実環境の承認条件が確認できなければ、その実操作と依存工程を保留して独立作業へ進む。

### 4. 後続PGPTと通常停止条件

拒否PTの再試行や全体停止を反復せず、許可されたPG実装→強化レビュー／静的チェック→対象別代替確認→依存しない後続PGPTへ進む。通常の小区切り・報告・限定照合終了は全体停止理由ではない。独立作業が尽き、残件が拒否操作又は未解決の必須条件にだけ依存する時に限り、対象と必要判断を報告する。

元PGPT計画のscope・モデル分担・原見積り／v3／v4・群開始予算・同source／重複費防止・通常残10%停止・reset／追加課金禁止は維持する。代替確認の費用を実行していないPTの実費へ見せかけず、レビュー・静的check・追加発見・手戻りを分ける。工数率と専有費不明値はnull。

今回の再開は本承認を含む新プロンプトを利用者が既存PGPTへ投入して行う。プロンプト作成だけでPMOが対象を起動せず、拒否の解除やPGPT完了を推定しない。PMO監査の再開はその指示・設定を別途確認し、限定作業の終了や単なるidleだけで実施全体停止と判断しない。

## 2026-10-18明示再開・予実比較補足

利用者の`work/PMO/hourly-monitor/resume-prompt-20261018.txt`全文を現行指示として適用。停止条件は下記通常10%（該当短期窓を含む）、reset券/課金0。原見積・10/10v3・過去群開始見積は固定し、v4残313.71/597.25/1426.07ppは未較正暫定予測であり実費・完成率ではない。活動群で正確な主担当leaf/残工程/個別criteria/終了依存/次証拠/開始見積を固定、終了時に前回計画完了・追加発見・手戻り・source再認証・見積条件訂正を区別する。不明な計画消化率/実N/T/専有費はnull。現保存点/未実施順序は最新456/460を優先し、完了済3791/独立資格/署名/ABIを再演しない。

## 現行：2026-10-17利用者訂正、通常残10%停止へ復帰

利用者はPMOチャットのuser turn `01a14807-20b9-77a1-9b5b-dc0844106d0a`で「リセットチケットがあったので臨時のオペレーションでした。通常は10%停止が正解です」と明示訂正。実施側は同user原文をread_threadで確認し、PMOからの今回送信を受領した。**10/10の残3%先行保全・残1%停止overrideは券があった臨時回限りで失効し、今回/以後へ持ち越さない。** この現行条項が下記履歴と過去456/460の残1%表記より優先する。

通常は週次又は実行を制約する短期枠の**残10%以下で新製造・新試験（全回帰/native含む）・署名・unused/RO/有限公開・Root/VM変更等の新工程を開始しない**。必要最小限の元job結果回収・所有/現況の読取・証跡/差分/計測cursor・checkpoint/次command保存を行い停止する。fresh使用95%/残5%/reset1792649711/券0の今回も保全停止し、PGPT完了ではなく未完繰越とする。既実行jobの結果を破棄/正常化せず、二重起動やPIDだけの操作0。自動reset/追加課金/枠回復だけの自動再開0、PMO毎時監査PAUSED維持。モデル/thinking・scope・451品質/受入は変更しない。

## 履歴：2026-10-10 利用者承認v3・臨時override（2026-10-17失効）

以下のoverride/券条項は当時の比較履歴として保全するだけで、現在の実行許可・停止条件ではない。

残予測はPMO `wbs-reestimate-v3-PGPT-20261008-PG500.json` / `PMO-remaining-v3-20261010` / SHA256 `6f7faa627cf64a1496dd980faf59406170e3458d00773fc7e8d83bf754f98298`、低310.68/標準586.75/高1297.64週次共有pp。下記当初90.90/269.80/642.60と過去群開始見積りは比較履歴として維持。252leaf（実251＋予備1）、190元/83子/共有主担当/参照費0、品質・受入不変更。

今回だけ実施側停止規則を週次残>1%で安全な小群を継続、<=3%で先行保全、fresh<=1%で新製造/試験/VM変更停止へ置換する。指定既存reset券を最大一枚、利用者指定 `reset_credit.py status/redeem --checkpoint .../pgpt-reset-control/reset-ready-checkpoint.json` の正規手順でのみ消費可能。policy/stateを変更せず、同UUID/creditの一論理消費を保持。receipt `continueAllowed=true` とfresh枠回復の両方を確認後に同chatで続行。reset前後は別窓・消費相殺/実token捏造/成果再加算0。対象外/取得・操作不能/短期先行制約では保全報告、券使用後再度<=1では停止。二枚目/新券/追加課金0。従来10/5・自動reset禁止は今回実施側には適用しない。

PMO毎時監査はPAUSEDを維持し、再開・閾値変更・hourly-monitor編集0。PGPT event/usageは既存cursorで増分保存。G13.07初期join→各領域開始join→最終release差分、群開始leaf/stage/見積版/hash/予算subset/次証拠、終了実績/残工程差を保存。N/P/CHR/K01/G費用を重複計上せず、K01標準12campaign/35pp・triggerなし全回帰0。89pp×99%=88.11は過去cycle限定仮定で個別実費ではない。通常commit/小受入/報告/PMO待ちで停止しない。

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
