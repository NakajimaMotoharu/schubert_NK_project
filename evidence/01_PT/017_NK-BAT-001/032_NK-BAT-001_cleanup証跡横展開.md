# NK-BAT-001 cleanup証跡・共有inventory横展開

PG164/SSC057、BUG179/YKT140は先行fac8438e、BUG180/YKT141は先行231b948f。2026-09-13。正式認定前candidateのPT側不備でありProduction/DDL/独立期待値を変更していない。正式回帰までは対応中。

## 1. BUG179・YKT140 — 実値の起点

PG164全5 Java trace＋1 SQL trace、隣接PG163全2 traceを対象に、trace/append/Files.writeStringの引数をread-only検索後、起点を個別確認した。期待literalは020/026、別canaryの019へ固定し実値から生成しない。

| 対象/Test ID | 確認・修正内容 | 起点／非該当根拠 |
|---|---|---|
| BAT162 seven-kinds | 固定totals/deltasからのoutputを修正 | 実CleanupStepChunk.stepCounts/countsと実ENDのboolean |
| BAT165 jdbc | 固定53/53/3からのoutputを修正 | 実Probe.seen合計、実発火検証後のtried、2close発火確認後のpairs |
| BAT171 chunks | 固定1001/1000-1-0/171/0からのoutputを修正 | 実summary.after、実ResultSet deleted_countを借用probeで記録、実seen合計、実再開summary.callCounts |
| BAT173 jdbc | 固定115/115/1/0からのoutputを修正 | 別の正常実走seen合計、全故障発火確認後のcases、実commit不明後の再開before/callCounts |
| BAT177 service | 非該当、再試験 | adminの実SELECT terminal文字列をそのままtraceへ出力 |
| DB259 SQL | 非該当、再試験 | 実V020 SELECTの7列をactualへ読み、expected照合後actualをtraceへ出力 |
| BAT138 terminal（PG163） | 非該当、再試験 | 実SQL terminal値actualをtraceへ出力 |
| BAT150 JDBC（PG163） | 非該当、再試験 | 正常実seen合計/faultCount/実両close発火数 |

すべて公開合成fixture。8 traceは秘密data/credential/raw session/tokenを含まない。Java UUIDはテスト専用公開runのものでsessionではない。inputの固定期待値とoutputの実測値を別directoryへ収集しhashで束ねる。

## 2. BUG180・YKT141 — 全inventoryと所有

| 対象 | 確認・修正内容／対象外理由 | 再発防止check |
|---|---|---|
| 020個別Program3追加class | 値8/Repository8/Service8、BAT154～177の固定method列挙 | 019の別literalで32新PT（SQL8含む）の欠落/重複/未知/非PASSを拒否 |
| 020共有module所有 | 16 Program class＋9 OPS class=25、Batch247=Program177+OPS70 | 019旧22class/13件sliceを25/16へ是正、全25位置の欠落/未知/重複拒否 |
| 020.validate_reports | 16 class/177 IDで重複加算なし | 個別期待mapの177 ID、全16classごとの欠落/重複/未知拒否 |
| 018全scope/呼出順 | 新026/atomic-cleanupを追加し15collector/38scope | 別一覧38 scope、全38位置で収集失敗後の後続停止とhash/run/source一致 |
| 026 SQL8 | 新V020/DB259～266、7kind/10table component、固定trace | 019の独立SQL8一覧と1byte改変/欠落/追加拒否 |
| 025現行migration説明 | 現行20 inventoryへ追記 | 歴史18hashはそのまま、DB258/266で独立旧hash/全20 SQL＋1 SCHEMA |
| 019過去65/91/107/127等例 | 過去のownership計算回帰例は現行件数ではなく非該当 | 旧例を保持し現行247=177+70の独立例を追加 |
| 017既存canary | 既存scopeの個別traceチェックは変更不要 | 全1件を別実行、019の29件と合わせ30負canary |

## 3. 探索再試験（正式認定には未算入）

- Java探索1: /tmp/pgpt-atomic-cleanup-service-explore1.log、05:35:18 JST終了、19.643秒、exit0。新24件成功。ただしtrace出力起点はBUG179前。
- 修正後Java探索2: /tmp/pgpt-atomic-cleanup-service-explore2.log、05:39:39 JST終了、20.782秒、exit0。新24＋PG163既存24=Batch48とStorage8成功。全実trace一致。
- canary探索1: /tmp/pgpt-atomic-cleanup-canary-explore1.log、29件中error1で非合格、BUG180。失敗を合格へ混入しない。
- canary探索2: /tmp/pgpt-atomic-cleanup-canary-explore2.log、29件成功、exit0。017別1件も /tmp/pgpt-atomic-cleanup-trace-canary.log で成功。
- 最新結合選択実行: /tmp/pgpt-atomic-cleanup-combined-explore1.log、05:44:46 JST終了、39.764秒、exit0。API31（新SQL8/旧parent8/DDL15）＋Batch48（新24/旧24）とProtocol/Storage選択PT成功。4新class×8 methodの正規inventoryとPG164/PG163全8 actual traceを別collectorの固定literalへ照合しPASS。
- 原子SQLの追加境界: 17のpredicate代替×前後1µs/just=51組、候補rowを他TXで保持→ eligibleならLOCK_BUSY/unknown totals、解除後1件削除、非eligibleなら0END。Java UTC fullhandleは6歴史時刻×3timezone=18組の独立SQL fixtureで確認。
- 新5classは探索JaCoCoのline/method/class/branch全100%（5class/19method/148line/102branch）。CleanupKind既存2methodは選択試験対象外のためここで全module100%とはしない。正式clean verifyで既存PTも全走行する。
- 現在のsourceは未commit candidate、親HEAD231b948f。上記探索を正式targetCommitの証拠に流用しない。後続正式runのmanifestでsource/OS/JDK/command/日時/exit/coverage/static/trace SHA256を確定する。

## 4. 未完了

正式全reactor、38scope一式、30負canaryの同source再収集・hash検査まではBUG179～181・YKT140～142を完了にしない。PG164部品が合格しても親OS lock/実unit終端/実backup/全step・Question writer・pending revoke/実NK CHR・PGPT/IT/STは完了にしない。

## 5. BUG181・YKT142 — staticと未知例外保全

先行bd91ab10。探索static /tmp/pgpt-atomic-cleanup-static-explore1.log、05:46:47 JST/13.226秒/exit1、THROWS_METHOD_THROWS_RUNTIMEEXCEPTION 1件、error0。StepCleanupService.transactionの未知Runtime分類用pattern変数を直接throwする行が対象。SQLException/既知Repository/既知STOPは固定失敗、未知Runtime/NPE/Errorは元identityと固定suppressedのみを維持する仕様は変更しない。

- 対象: StepCleanupService.transactionのcleanup SQL失敗時。分類はinstanceofで行い、送出は元multi-catch変数を使用する。対象SQL/Repository/STOP/Runtime/NPE/Error×cleanupなし/rollback失敗/restore失敗の全18組をBAT176で再試験。無条件wrap/例外握潰し/追加review・suppression/coverage除外はしない。
- 非該当: 同cleanup packageのLogCleanupServiceは元failureのrethrowで新pattern再送出がなく、直前正式07 static未解決0。InspectorLockHandoff等他Productionは同正式07で合格し、今回全module static回帰で再検査する。
- 追加品質: 新Java24＋旧PG16324＋旧CleanupRepository17、計Batch65を選択し53/115 JDBC故障位置・3組double-close・30分/割込/18例外組/全新coverage/SpotBugsを再走予定。各scope manifestと本監査hashを正式runへ関連付ける。

最終探索再試験: /tmp/pgpt-atomic-cleanup-final-explore.log、2026-09-13 05:49:24 JST終了、39.399秒、exit0。Batch65＋Storage8成功、failed/error/skipped0。JaCoCo新5class/19method/145line/102branch missed0、共有CleanupKindの全5method/22line/6branchもmissed0。SpotBugs未解決0/error0、新除外なし。BUG181前の148lineは同sourceではない旧探索値として残し、現在の145lineと区別する。019/017負canary29＋1も再実行成功。正式回帰待ち、利用枠残46%。
