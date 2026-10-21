# Morning完了診断二次故障：独立PT仕様・開始記録

Program NK-OPS-001、MorningStartupLaunchOwner.CompletionProgress.failure/phase、OPS009/UI251/SS343354/SSC326/BUG1581/YKT1320。これは正常sourceレビューで発見したProduction不具合であり、実VM失敗や拒否PTとは断定しない。PGを省略せず独立PTを並行実施する。

## 先行設計・既成果

SS326は343/354/914だけのsource147cd7805、[PR188](https://github.com/NakajimaMotoharu/schubert_NK_project/pull/188)からmain111942b6775bf63f14fcd1088232c80cc205b8a5へmerge/remote確認済み。実装等混入0。attachment件数上限により紐付け一回失敗・再試行0。旧source669ad原4054/610/1667・資格/trace/auditは完了保存済みで、当新Testへ合算0。

6432通常client/control41警告の個別理由は[manifest](evidence/provisional/PG6432-control-client-static-review-v1/manifest.json) SHA `117fd6ab8314b631e762bb7a775b43f0f4ac0860f6a85ad775310676a395ae71`。正負二工具0、raw1358不変、未点検102→61/semantic不足12、実case再結合はまだ。後続50sourceレビューの途中でCompletionProgress→retain迂回を発見し、line395二警告を適合へ昇格しなかった。50群は未完のままBUG1581是正を先行し、費用・未完を隠さない。

## PT_DEFAULTの判定・独立期待値

pure Java自己所有clock/sink/counter/list/固定Throwableだけ。ネットワーク・DB・native・VM・service・実Root・failed-cohort・intent/permit操作0。新PTは拒否範囲探索や拒否PTの再送ではない。既4Testの正常literal/順序/null・境界期待値を変更せず、同Test class末尾に以下2methodだけ追加する。

|Test ID|入力・操作|独立期待値|
|---|---|---|
|COMPLETION326001|主障害IO/Runtime/Error × 二次sink/clock × RTE/Error、計12fixture。constructor時計のみ正常、failure通知時だけ故障。assertAllで12個を同一Test内で評価。|failure呼出は二次故障を外へthrowしない。時計2回、時計故障ならsink0、sink故障なら固定CADDY_BEFORE/IO・RUNTIME・FATAL/elapsed0の一行だけ。主/二次PRIVATE文字列不出力。12をPT12件へ水増ししない。|
|COMPLETION326002|phase(DONE_AFTER)へsink/clock×RTE/Error、計4fixture。|通常phaseは同一二次Throwableを伝播、時計2回。failureのbest-effortをphaseへ拡大しない。4をPT4件へ水増ししない。|

既COMPLETION790001～004のnull・固定期待値・全retirement境界/秘密不出力を保持。rawcoverageは原XMLのみ、未測定補完/除外追加0。診断封じは元catchのretainへ戻す局所契約であり、実親非復帰/所有/DB/Unit正常終端を証明しない。

## 実行予定

`PYTHONPATH=tools/quality:tools/quality/vm/050_s1:/home/mini/codex/project1/work/toolchain/pyflakes-3.4.0/runtime python3 -B tools/quality/pg6438_morning_diagnostic_red.py`

source=本Test/operator保存commit。Mainは旧669adと同byte、変更Test一pathのみのguard。新only pg6438-morning-diagnostic-red-v1、baseline12/7＋当6/1＝18/8、六format先行・型/null/既静的check・全Main compile。最初の失敗は既実装BUG1581の再現として保存し、同oracleを固定して一Main PG→関連23/10へ進む。既全4054を再演しない。JDK25.0.4/Maven3.9.12/既toolchain、formatter7840終了0、定義正負二0。赤PTはまだ未実行、source/command/exit/XML/hash/coverage/再現詳細は後続結果へ記録する。

fresh46残54/reset1793082864/短期不明、当追加発見群.5/1.5/4pp固定・通常50群未完・実N/T/専有費null。正式1964/53/17受入190作業/工数null/QA051final/PTALT不明代替0/実環境HOLD・全保全維持。通常区切りで停止しない。
