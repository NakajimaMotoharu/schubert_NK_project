# User監査closed request回収是正・全二十再資格

NK-ADM-001/ADM-AUDIT-PORT001..020、FUN009/MON004/UI226236/SS312323324332351352・411§10/451、既089/090のwhole UserCriticalAuditPortTestを継続。原見積2/5/9pp cap10、是正費主WBS-F03、元code owner P01003/Query P01001は参照費0。

発見は原PG22382 CloseResource一site、Test.audit016のclosed request宣言後にfinally回収なし。411はclose後の検査もplain try/finally回収を要求する。修正前BUG/YKTへ登録し、元Test/原raw/同source成功19668を保全。closed.close→closed request拒否assertionと末尾資源assertは保持し、当scopeをtry/finallyで囲みfinallyからidempotent closeを呼ぶ。他19method/既固定SQL/JSON/入力/expectedを変更しない。Main全不変更。SS/QA変更不要。

既原089のwhole20 graphを確認し、同じborrowed JDBC Proxy/公開固定DTO/三writerへ限定する。UserMutationRequest.closeは公開配列消去とbooleanだけのidempotent処理。SQL/DB/crypto/認証/正規user更新/Root/VM/native/四guarded型の初期化実行なし。元Testの切出し/新fixture化はせず、変更した全20methodを新sourceで一回再資格する。正常Main7aed/22084と六静的22086はbyte一致だけ再利用し再buildしない。

新sourceのlint/Werror・GJF/PMD/CSを実施、rawは当Test一file別XMLへ保持。適用0/非該当理由を一siteずつ確認し、元85 raw347を上書きしない。他84fileは入力hash/tool/rule/sourceが一致する範囲だけ歴史subproofを保持。当sourceのUserAudit rawと既2loader/4threadの個別理由を新位置/byteへ再束縛し、未知Map一件は未分類のまま。原体の347/265/82を無条件で新sourceへ流用しない。

source固定push後、JUnit全20/F-E-S-abort0/OS0、六physical/CRC/一exec-session/全Code L154M20C5B68（standard SwitchMap noCode1・enum/TWR raw未達は元値保持）を独立確認する。元execを合算しない。新20は既20の再資格で新unique0/source追加0、正式1964PT/53scope/unique430/whole94/新leaf0/工数null・全HOLD/451全体不変。失敗/欠測は保持し修正前台帳、通常小区切り停止不可。
