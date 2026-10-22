# 次ordinary候補・管理停止結果の分離計画（準備、未着手）

現6768/Source d549のMain/Testは固定する。この資料は原4197/同source品質/traceの後に進む候補の分解で、群開始・新PG/PT・受入・見積減額0。基準測定は旧bad7原4189だが、以下対象のsource hashは現candidateと完全一致を確認した。現4197実counterで再照合後に着手する。

## 実安全条件を要する候補は保留

- P004-04 InspectorApplicationの残11L/1MはexecuteNative。固定identity/実ChildStartupContext/INVOCATION_ID/credential rootのownerを必要とする。既データ/guard port試験をnative入口実証へ外挿せず、actual起動/権限/原本はHOLD。
- P017-05 MorningBackupRetentionの残20L/3Mは固定backup root/実backup identityを所有してcollect/再確認するuse側。自己所有普通collect試験と実rootの運用を混同しない。actual Root/Backup/DB/退役等HOLDは継続。
- NativeCoveragePrivateFile/FixedNativeCoverageCheckpointの固定agent/root/run/export側、WebTerminalCapture.currentJvmの実stop hold接続はRoot/Native条件へ依存。pin pathの偽装・別routeのexport・native成功の補完を行わない。

## 独立候補：WebManagementServerの停止結果共有

P018-06（着手時は484の実leaf確認）。原counterはline70 `result.close()`の通常帰還側1L未網羅、全method/branch既網羅。既ready007 CompoundFailureServerの空secondaryを含む八inputは実際にcloseを一回呼んで固定IOExceptionをsuppressedへ保持するが、start失敗ではstarted=falseなのでSSC317どおりcloseは未確認IOExceptionを返す。calleeの暗黙例外でそのinvoke行の通常帰還probeが残る。private started反射・擬似成功・到達不能除外・coverage数値補完で100にしない。重複する同一fixtureを追加しても実意味のある検証増分にならない。

内部PG候補は停止機構を一つの`Optional<IOException>`結果へ分離すること。既public/package closeWithinはその結果があれば同じIOExceptionをthrowし、openの起動失敗処理は同じ結果を元failureへsuppressedとして保持する。停止の確認／未確認が普通の内部値になり、通常closeと起動失敗cleanupが同じstate machineを通る。公開API・起動/stop回数・state/期限/割込/診断と元Error優先を変えない。単にprobeを移すのでなく、想定内の未確認状態をthrow-catchで往復させない責務分離として、全既独立oracleで反証する。

|状態/操作|維持する独立期待値|
|---|---|
|未起動/起動失敗のstop要求正常帰還|started=falseなので未確認、closedをtrueにしない、fixed IOException Web management stop unconfirmed。ready=false|
|started/stop正常/実executor終了|serverStopped=true、closed=true、再closeはstop二重発行0|
|executor非終端/期限又は割込|同fixed IO未確認、割込を保持、正常終了へ読み替え0|
|primary Runtime＋cleanup Error|元cleanup Errorが優先、元primaryへのsuppressed追加0|
|primary Error＋cleanup Runtime/Error別object|元primary Error優先、取得前preallocated fixed diagnosticだけ保持、private cleanup causeを外へ保存0|
|primaryとcleanup同一object|自己suppressedを行わず元identityを保持|
|normal cleanup由来のfixed IO|元primary identityを保持、当fixed IOExceptionをsuppressedへ一回だけ、cause null|

Source code上、closeWithinのchecked IOは上記内部状態から作る固定例外だけで、HttpServer.stopはchecked IOを宣言せず、その他Runtime/Errorは従来どおり外へ伝播する。この境界を維持し、確認不能を成功にしない。stopLock/Atomic flag/準備順/親owned責務・30秒上限・public JSON/HTTP/Prometheusは不変更。実業務Web/Unit/Caddy/Root/VM/credential/原本とは独立した既factory stub＋自己所有ephemeral HTTP/executorだけのPT_DEFAULT候補。

着手時には必要915/916/判断を先行し、全既WebManagementServerTest/Unstarted/RuntimeStop等の適用性とsource exactを確認、着手前予算/具体command・独立仕様を固定する。新入力を無理に追加せず、既oracleで新PGの意味を確認する。SS範囲内の内部詳細ならQA不要だが、外部stateや例外表変更が必要ならSSC/QAを先行する。実Source未変更・未実行、正式/17/工数null/全HOLD/PTALT代替0/QA051final/原-v4は維持、通常区切り停止0。
