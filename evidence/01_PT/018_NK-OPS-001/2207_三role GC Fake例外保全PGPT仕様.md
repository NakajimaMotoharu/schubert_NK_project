# 2207 三role GC Fake例外保全PGPT仕様

NK-OPS-001/WBS-F03、群THREE_ROLE_GC_FAKE_GUARD_PGPT_V1/event2568・原2/5/9共有pp cap10・使用34/reset1793599188。BUG1913/YKT1662/PG-D706、SS351/411・1785/1787/2206、sourceBefore2d733dbd8。

F03-GCFAKE001：各Fake取得八箇所に宣言直後plain try/finally、未確認候補だけclose。one/twoは二の取得失敗でも一を保持し逆順cleanup、元body/明示owner close/元identity/各10秒を維持。Fakeにprimitive closeConfirmed（初期false）、close callback正常帰還後だけtrue、失敗はfalseを保つ。元42methodの全oracleは追加wrapper/fieldだけ逆除去して一致、各guard欠落/別候補/先行確認/期待/期限変異を拒否、Main/他input不変。

002：各元gc001..014＋新gc015016＝48/三suiteだけ一ja-JP JVM/一exec。015はfresh未確認→close成功→確認済みcleanup skip・close計一、016はRuntime/Error callback失敗のidentity/未確認/close一→callback解除/明示retryで確認/close二を独立literal/countで検証する。finallyはcallbackを無害化し未確認候補だけ回収、失敗をPASSへ変換するcatchやNPE正常化0。新Test ID六、既42は変更影響の必要回帰、旧成功を算術加算しない。

003：normal六module package/Enforcer・format・NullAway・Werror/PT0→閉48 catalog/自動extension・parallel・package discovery無効/own空CWD/JVM240秒。元real001は新自己JVM GC handleを保持後だけbind/同Testでclose、他Fakeはlistener activation0。GC強制・外部process/HTTP/DB/JMS/VM/Root/鍵/旧handle/保留工具・Graph9/deferred8操作0。論理確認flagは本Fake callback完了だけで、実SDK/業務worker終端の証明にしない。

004：当三Testの実PMD/CS/processingと残rawを保持。一exec/session/CRCを完全API467/Web358/Batch645へ個別読取、三GC Main四counterと全artifact未達/全1843Main・他Testbyte/三SourceFile物理差を照合する。元canonical owner/cost/全歴史・予算/全WBS audit真正状態・command/env/exit/hashを2208へ結合、全YKT対象と追加case・BUG再試験まで当scopeを閉じない。正式1964-53/17-190/工数null/QA051final/全安全HOLD不変。
