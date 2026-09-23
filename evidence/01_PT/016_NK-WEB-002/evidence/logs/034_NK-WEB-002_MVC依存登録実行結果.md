# NK-WEB-002 MVC依存登録実行結果

PG227/PT-SCR120～123は正式`PT-WEB-20260924-17`/source`be6379ccec237f594b8987de7e53d27f71c3cec2`で限定認定。全1778PT（CHR41/Protocol80/Storage82/API699/Web504/Batch372）、failed/error/skipped0、Java6 module instruction/line/method/class/branch missed0、Production SpotBugs0、90負canary、44scope/hash・保存manifest再照合PASS。root manifest SHA-256 `5a94bfcda78ed140625de248f8c02a43ca87832d17c9a98ef311587df43170cd`。016証跡の`results.xml`に新4 Test IDを一意記載し、各JUnit/coverage/OS・JDK・tool・branch・commit・command・終了code・入力/期待/実際・hashは`evidence/manifest.json`を正とする。新`WebHttpServer` instruction347/347・branch24/24・line81/81・method11/11・class1/1。実HTTPのcaller-owned port応答、起動前の型/null拒否、旧factory起動成功を確認した。

履歴: run15はMaven成功だが006 collectorのWeb instruction未網羅2で不認定し、旧factory成功戻りのPT-SCR123を追加した。run16/source`e5204fc7`もMaven成功/全1778PTだが029旧固定Test ID表に新120～123がなく、44scope未認定。いずれも合格に算入しない。実NK CHR-L01、Web reply/Log worker親起動、NK-WEB-002全体は未完了。
