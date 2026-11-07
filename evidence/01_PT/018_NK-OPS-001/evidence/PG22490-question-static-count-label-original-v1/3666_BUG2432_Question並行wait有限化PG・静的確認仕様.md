# BUG2432 Question並行wait有限化PG・静的確認仕様

WBS-F03/REWORK、411/451/SS352、BUG2432/YKT2177。新群原1/3/6pp cap8、前群1/3/7/追加発見費を変更しない。現在QuestionControllerTestは元sourceでjob.get()無期限一箇所、元whole実行はHOLDであり本群でも再実行しない。

PG対象はrcpt006Hのjob.get()を、同file先行並行Testと同じget(10, TimeUnit.SECONDS)にする一箇所だけ。Fixture/入力/oracle/全assertion/他method/Production sourceを変えない。原Testを保持し、GJF skip-reflow明示とJava token差分で一callの引数追加だけを独立確認する。新fixture、Test compile/Unit/DB/session/Root/VM/native/拒否操作は行わない。

許可済staticは対象fileだけのPMD/Checkstyle・parse-only AST、既正常Main/工具/rule/auxへ同hash束縛。Test file全体がHOLDであることを変えず、元120s等の外側run期限やexecutor停止・実livenessを本get変更だけで認定しない。code修正/静的確認済・動的再試験NOT_RUN_HOLDとしてBUGを残し、CLOSED/PASS/coverage/正式受入を捏造しない。

current85 subsetの当file以外84は同hashを確認し、現UserAudit是正sourceを含めた新構成raw/19既分類の新位置への束縛を行う。旧Questionの20指摘とvolatile12/loader/thread根拠は、修正がget引数一箇所だけで他statement/method/decl/writeが不変と証明できたものだけ再資格する。元347/current構成346を上書きしない。Map62/reflect1と全F03/451は未受入。

再発防止のstatic guardは、元unbounded正形を拒否し、新bounded一call/peerの10SECONDS・全他token保持・ASTのunbounded-get消失を確認する。YKT2177の全85既明示Testの他Future待ちsource調査は別群で、検索だけで閉鎖しない。unique430/whole94/正式1964PT-53scope/新leaf0/工数null・全HOLD/モデル/料金条件不変。
