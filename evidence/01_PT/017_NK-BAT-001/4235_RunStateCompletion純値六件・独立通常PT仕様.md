# RunState / Completion純値6件・独立通常PT仕様

NK-BAT-001、WBS-P017-02/P017-12、OPS009/UI251/SS331/341/343§6.13/6.15。対象MaintenanceRunState/MaintenanceCompletion/Outcomeと既BatchRun/MaintenanceActivation。費用F03追加資格.3/.9/1.8、原費用・既S/V上限は不変更。

PT-BAT-RUNSTATE-001: 固定synthetic run/activationとOptional.empty、activation/empty及び固定redactionを確認。
002: 同値で別instanceのactivationに対応するcompletionを許容し、Optional内値・activation/id・cutoff/ended/outcomeを固定入力と比較。
003: activationIDだけ違う・runIDだけ違う・cutoffだけ違う三不一致completionはIllegalArgumentException。旧Original/DB/runtimeの所有を値から推定しない。
004: Stateのactivation/Optional及びCompletionのactivation/ended/outcomeのnullはconstructor invariant拒否。NPE catch正常化は行わない。
005: completion時刻はcutoff同時とUTC9999-12-31T23:59:59.999999Zを許容、cutoff前1µs/年10000/nano1を拒否。期待は承認されたUTC年/µs契約のliteralでproductionから生成しない。
006: Outcome閉集合SUCCESS/WARNINGと終了code0/10、Completion固定redaction・全accessor。未知値を既成功とみなさない。

既whole BatchRunValueBoundaryTest原2は固定literalの年/µs/null/JST日付を同runで補助回帰する。新whole6を既2成功へ算術加算せず、sourceを固定したwhole8の真正XML・終了・CRC・初期化・全5physical/四counter・全静的を独立確認。新record Testは実Root/原本/DB/ファイル/permit退役のTestの抽出や代替ではなく、public不変値のconstructor契約だけを独立に追加する。既全体/Native/CHR/実所有/未測定scopeのHOLD・451・元190正式認定は維持する。

Main4/Test2全sourceのJDK/JSpecify/JUnitだけ。反射、worker、network、DB、native、原本/鍵/intent/permit/VM/service操作なし。共通閉host profile prestyle→RootNullAway prepare→全静的→適用性→preflight→Git固定→一whole8→独立post。到達不能・除外でcoverageを上げず、未網羅/失敗/未実行はそのまま保存する。
