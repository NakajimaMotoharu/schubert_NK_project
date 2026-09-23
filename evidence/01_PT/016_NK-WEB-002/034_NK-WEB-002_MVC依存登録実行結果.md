# NK-WEB-002 MVC依存登録実行結果

PG227/PT-SCR120～123。正式run`PT-WEB-20260924-15`はMaven全reactor成功だが、006証跡collectorのWeb instruction coverage2命令不足で不認定。旧factory overloadの成功戻り未試験にPT-SCR123を追加した。run`PT-WEB-20260924-16`/source`e5204fc7`はMaven全reactor成功、全1778PT・失敗/error/skipped0だが、029画面証跡の旧固定Test ID表が新120～123を含まず、44scopeを認定しない。選択`WebHttpServerTest`7件＋`WebApplicationTest`4件、計11件成功・failed/error/skipped0、WebHttpServer instruction347/347・branch24/24・line81/81・method11/11・class1/1。collectorのTest ID 4件とProgram正本033/034を同sourceへ揃えてから新runで再検証する。実NK CHR-L01、Web reply/Log worker親起動、NK-WEB-002全体は未完了。
