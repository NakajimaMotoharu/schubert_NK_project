# Runtime dependency canaryのscope是正

Program NK-OPS-001/PT-BAT-283/新PT-BAT-283B、SS311 SSC088/411/451・BUG1463/YKT1227。原Source2fcの全3904はF1で保持、oracle変更の根拠はSSのMain/runtime依存境界とtest自身のJavadoc/既direct-setのtest除外である。期待するMain起動宣言**一件**を変更しない。

OPS-CANARY001：dependencyBlockがtest scopeをMain集計から除き、runtime/compile Mainの欠落・重複・誤scopeは従来どおり拒否する。fixture宣言は独立にat most one、type=test-jar、same project version、alternate classifier無しを検査。禁止API/Web/Protocol依存や未知Main依存の既否定は維持する。

OPS-CANARY002：新bat283bが手書きliteral POMだけでMain一＋test fixture一を区別し、Main無し/Main重複/test fixture重複/fixture誤runtime・compile・scope欠落/type jar・type欠落/foreign version/classifierを拒否する。expectedは固定literalのMain宣言でありProduction処理を期待値作成に使わない。actualPOMへの正常判定と全既BAT283 negativeも必要。

OPS-CANARY003：原monitor四owner/依存71にCanary全二caseを加え**新選択73件9suite**、全六format先行/NullAway-Werror/SpotBugs・全1664physicalを当snapshotで確認する。Source Mainは2fcと完全同じで、旧71結果を新source成功と偽らない。各actual command/commit/XML/hashは1154へ追補。`pg5566_private_monitor_selected.py green --version v3 --include-runtime-canary`をcommit/push clean後の新only一回とする。

OPS-CANARY004：選択成功後、静的bytecode事実のsource/class再bindingを行い、所定の新Source全3905/563/1664を一回完走・独立資格する。失敗3904の部分合格や旧source nativeを新wholeへ合算0。PG5574/76/78はまだ未発行なので新正当sourceへ初回発行前に再束縛し、旧未使用準備を実成功としない。元5572 source/run/outputの上書き/再演0。
