# 2632 現六host七十一件 限定registry・WBS参照結果

2026-10-30 JST、dev-foundation、開発source6b53/保存基点814e95126992d7d8a2f456c002b44caa58a26d9d。2631/PG-D880、群3018開始0.25/1.5/3pp cap10。元試験・成功確認の再実行0、新製品PT0、全証拠は既完了原runと現在sourceを結合したmetadata-only。

## 実command・証跡

各commandは `python3 -B tools/quality/pg11123_checked_python_entry.py tools/quality/<entry>`。

|役割/entry|実終了|公開provisional run / manifest SHA256|
|---|---|---|
|registry/pg14302_current_six_host71_registry.py|0|PG14302-current-six-host71-registry-v1 / 6fff0d2718570d7f15f6c2427163a7226ababd28656d23960cea3f54b66a852d|
|独立XML/pg14304_current_six_host71_registry_post.py|0|PG14304-current-six-host71-registry-post-v1 / e9fdba39311c8eb9d5f1ec61f448423e8d210eb98fa105ab2eb3c4dbedb17002|
|二WBS side/pg14306_current_six_host71_wbs.py|0|PG14306-current-six-host71-wbs-v1 / b52756616db36b3e15c1f92240d0e00bca4c325b8bb3b29ce05ced4232ca5190|
|独立WBS/pg14308_current_six_host71_wbs_post.py|0|PG14308-current-six-host71-wbs-post-v1 / 8a735aa7e8309e7b1ec300b837e81f8cab61726cad035fb49eded941897dcfbd|

全pathは `evidence/01_PT/018_NK-OPS-001/evidence/provisional/<run>/manifest.json`。14308初稿はimport置換漏れをpyflakesで検知しbodyStarted=false/未実行、その後初回bodyのみ実0。session9589内の後続sha表示commandは誤った486名により外側終了1だが14308 bodyExit0を別記、正しい486_WBS現行実績.jsonは下記hashで回収・再実行0。工具準備手戻りを元PT費へ隠さない。

## 照合された範囲

元14244/54/58/72/94/98の六post/元XML71・10suiteを一意join、17完全Source/21physicalを各元execに保持。四counter100九Source13physical、自然branch0六Source6physical（三counter100）・noCode interface一Source一physical・Inbound未達一Source一physical（L10/M2miss）。unknown owner12/全27pathを保持。旧0061の400/旧995runtimeの資格・費用・受入を移植0、原14260の15と14264 sideは履歴のまま。

独立registry14metadata負例と独立WBS12反例が件数/元source/old-transfer/owner/自然0/noCode/未達/正式昇格の偽装を拒否。485/486は既二sectionへtypedGuardCurrentHostPG14306Overlayだけ追加、486はinventorySha256のみを再束縛。全旧semantic・master481484・予算/受入不変。
- 485 SHA256 `94affeca110c84ab6effde2607faff62e02804bd67716997e135b00f49efccbf`
- 486 SHA256 `82bb09cc90439d5bd48fae7e512b81cb5e7957a849c009e4ba41d061fa9e3c67`

所定whole WBS auditは前後とも真正1/HOLD（current physical candidate exact Git/worktree scope）。限定metadata writer/post0を全監査成功に読み替えない。歴史ID参照3682/noRef2565は不変、現Source全体のformal・coverage受入ではない。正式1964/53、個別17/190、工数null、QA051final、BUG2092/93の動的HOLD、全F03/451/HOLD・原本保全を維持。外部actual操作0、二held工具は名前除外後metadata未読。
