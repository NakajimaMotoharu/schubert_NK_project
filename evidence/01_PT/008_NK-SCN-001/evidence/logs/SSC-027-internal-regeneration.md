# SSC-027 同Message排他・file確認/再生成の内部PG/PT

起票commit: aa881f2（実装前）。対象Test ID: PT-SCN-009-G01～G03、F01～F03、V01～V03、S06。段階service/DB descriptor置換/JMS接続とstartup強制は未完了で、この証跡だけでSSC-027/Programを完了にしない。

期待値: Gはlatchと独立した副作用counter/要求別戻り値、FはUI234の手組4800byte recordをJCAでhash、S06はUI232/234手組全wire＋独立JCE/LP-AAD復号、Vはlocal ext4上の4800byte固定patternの実属性/EOF/独立hash。Vのpatternはrecord codecの正常性oracleではない。Fのpublisher stubは物理write/欠落検査の代替ではなく、V・既存writerと区別する。

追加10 method: guard3、regenerator3、ready inspector3、snapshot置換1。Regeneratorは1/201/10000件を元hash/全8metadataへ照合し、32 digest位置の不一致・変更master・不正返却・容量/crypto/provider/I/Oを拒否。Providerが保持した一時4800byte bufferも失敗時zero化。Vは最大48MB・100並行、date/entry不在、リンク/属性/hash/size・callback内MISSING/close故障を検証。S06では元header（古いcontextを含む保存結果）、完了時刻・state/refを保持し、利用者へ返す新headerとは区別する。

初回探索で検出した新PT fixtureの問題（正式合格に算入しない）:

- F02のprevious/next IDとtitleを片側だけ付けたfixtureは既存paired契約で生成時拒否された。承認済み期待を変更せず、元snapshotにも対のある独立wireを用意し、正当な対を保持したまま8論理fieldを一つずつ変更するfixtureへ修正。これにより比較/hash/publisher前拒否の狙いへ到達する。
- V01の新FD監視proxyがkernel close後に番号を台帳から除去し、並行openで再利用された番号の新所有まで消していた。Failure stackはtest proxyのlive.remove assertion。DirectoryCallsのcloseは失敗時も所有消費という既存契約に合わせ、kernel close前に旧所有を除去する。Productionのclose動作・期待FD残留0は変更せず、並行実体I/Oも直列化しない。
- Resource宣言をdate生成箇所へまとめ、root検査失敗とdate/entry不在を別の所有scopeにした。Coverage除外、NULL resource捏造、到達不能扱いは追加しない。

対象範囲の探索は18関連method成功（既存delivery3、snapshot6、guard3、regenerator3、inspector3）。正式source commit・時刻・環境・command・全reactor結果・coverage・sanitized JUnit/hashは次の正式runのmanifest/002実行結果へ記録する。秘密情報/raw body/DB dump/実masterは本証跡へ保存しない。
