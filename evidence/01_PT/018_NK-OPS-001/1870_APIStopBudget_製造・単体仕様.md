# API停止予算・製造/単体仕様

2026-10-25/WBS-P018-05/group2102/PG-D637、P018-09の必要依存・追加予算0。開始3/5/9pp/cap10/fresh57残43/reset1793382075、元/v4/v5不変更。Program NK-OPS-001/class bootstrap.ApiStopBudget ctor/begin/remainingNanos/time、RD171/UI252/SS342§4.2・351、現依存1867/1869。既API60秒を最初のJava側停止通知から固定する内部primitive clock ownerであり、親30分/Systemdの先行TERM時刻と一致したとの保証や実停止資格を追加しない。現Lifetime/caller/Manager/Outboxへの供給は後続未接続HOLD。

最初beginは時計読取前にclaim、同時/再通知でrenew0。remainingはbegin前拒否、単調差分で60秒から減らし、正当なnanoTime wrapを許容。期限/逆行/signed horizon不明はsticky0、clock RTE/Errorは同objectを正常化せずthrowして以後0。finallyだけでinvariant確立しNPEをcatchして正常化0、null portはctor境界拒否。借用原期限を延長せず新Thread/Hook/TERM/VM/DB/Root/配備/既サービス操作0。plain primitive stateとclock portだけ、close/lifecycle resourceなし。

期待値は以下の独立literal（60_000_000_000ns）とJava signed64bit算術、production定数・methodで算出0。普通JUnit APISTOP001～018、新fixture Executorは自己所有で有限回収、既ApiProcessLifetimeTestのHookDriver/TERMを選択しない。

| ID末尾 | 入力/操作 | 独立期待/観点 |
|---|---|---|
| 001 | ctor null clock | NPE/未取得 |
| 002 | ctor clock counter | 未読0 |
| 003 | begin前remaining | 固定IllegalStateException/未読0 |
| 004 | start/current7 | 60_000_000_000/時計計2 |
| 005 | begin0→current9→再begin | 再begin未読/59_999_999_991 |
| 006 | 経過0/1/1e9/59_999_999_999 | 60e9/59_999_999_999/59e9/1 |
| 007 | 経過60e9→時計0 | 0/0、expiry後未読 |
| 008 | 60e9+1/MAX | 0、overflowで正値復活0 |
| 009 | 開始100→99→101 | 0/0、逆行後復活0 |
| 010 | 開始MAX-10→MIN+9 | 差分20/残59_999_999_980 |
| 011/012 | 初回begin RTE/Error | 同object、再begin未読/残0 |
| 013/014 | remaining時計RTE/Error | 同object、以後未読/残0 |
| 015 | 初回clock保持中の二begin | 初回claim一/時計一、自己Executor回収 |
| 016 | 開始0/時計0/8同時remaining | 全60e9/計9時計read |
| 017 | 開始MIN→0のsigned半周以上 | 差分MINは不明扱い0 |
| 018 | 期限後faultを仕込んで再begin/read | fault未読/期限0のまま |

実command/source/環境/開始終了code/XML/四coverage/static/CRC/session/hashは1871とmanifestへ。新sourceの当一Main全counter100/全分岐/NPE静的+negative・独立oracle・source/run一致を要求、metadata反例をPTへ加点0。trace canonical ownerは既ApiProcessLifetimeと同P018-05を根拠に明示しP018-09変更元から推定しない。初回 source/成功を別sourceへ移植0、正式1964-53/原190新受入0/工数null/QA051final/全actualHOLDを維持。
