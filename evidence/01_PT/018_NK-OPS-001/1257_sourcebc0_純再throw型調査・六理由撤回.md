# 1257 sourcebc0：純再throw型調査・六理由撤回

群PURE_RETHROW_PG_SURVEY/event1445、WBS-F03、着手見積0.25/0.75/2共有pp固定。Production **bc0cac2f6a7055b938f581e8cd163db398f8a656**/Main/Test変更0、元全6014は固定して継続。実N/T/専有費/工数null、原v3v4維持。

新SourcePureRethrowInventoryはJDK25のJavacTask parse/analyzeだけ（proc:none/implicit:none、Production未実行）。独立fixtureで純parameter一文だけの再throwと、cleanup/代入/別throw/括弧/lambda/checked例外/後続Exception・Throwable/残try成立を区別。実Main-only851source/1666class・1094catchを型解決、compile/独立fixture/actual0。WorkPG379/pg6018-pure-rethrow-facts-v1/manifest.safe.json SHA **a41aa68e00e35d3430b10043d9e7db5f8bfb9ef35add69630dfc80686185178e**、pure16/root115/後段包含44、全catch除去候補1。finalDirectだけの候補抽出は行わず、Source/testが未確認のPGを省略して受入0。

各union成分へ精密化し、固定JDK javap実階層(Error→Throwable、RuntimeException→Exception→Throwable)を独立表と照合すると、WebBrokerContexts.closeの純Error catch一件は除去候補、ArtemisManagementReadinessClientの五unionはRuntimeだけ残す候補。LinuxSystemdSession.Native.invokeは後段Throwableが両型を捕捉するため維持する。六候補すべてのError診断には旧REQUIRED_CONTRACT理由が付いていたが、「後段ExceptionからErrorを保護する」は誤った必要性判断。現在の処理結果は正しく、冗長catch/根拠誤認であり未知Errorを握潰した発見ではない。

BUG1523/YKT1283を先行起票し、旧6012 artifactを不変保持した追記 `evidence/provisional/PG6020-rethrow-review-withdrawal-v1/manifest.json` SHA **fa2b2e407ab6fc6a303e34f5a323a2810a6f2b0125b23577d26c92205b4e6bd4**、inventory SHA **694842a783cb3b90718489fdfd4c40395d8f37f836a11fa496fe3c7fc8f3bdde**、actions SHA **3cc6d7aa946f87a5778486272fc8f51f60c98902484996b4a1f8f9c1683386b8** で六理由を未reviewへ撤回。**630新whole待ち/718未review/raw1348全保持**、新accepted0・新PT0・PT代替0。旧636から6減は進捗でなく誤判断の訂正。個別source/method/UTF16範囲/type成分/後段型/旧理由はactionsと旧manifestへ一意追跡する。

撤回工具の初回はrawの可変statusまで同値比較してactual1、v2はPMDのError span末尾spaceを語そのものと比較してactual1、双方出力前停止/誤撤回0。BUG1524/YKT1284、1525/YKT1285を各修正前に登録し、原工具/testをWorkPG379/pg6020-original-raw-guard-v1（tool6220e95b/testfeecbc69）、pg6020-v2-selection-guard-v1（tool724f79b6/testb7cf66b5）へ保持。13不変raw field/ID順序と分類statusを分離し、Error tokenは周囲whitespace除去だけ＋固定実診断本文SHAを照合。四独立unitで源/座標/hash/ordinal/schema/重複順序・後段Throwable/型包含不整合/別token・別本文を拒否、実全1348/六撤回0。原診断座標・本文hash・源・Test・期待値は不変、PT/VM再演0。

SourcePure helper/fixtureの定義unitと新engine二unit0、実command=`python3 -B tools/quality/pg6018_pure_rethrow_facts.py`、撤回=`python3 -B tools/quality/pg6020_rethrow_review_withdrawal.py`（既PYTHONPATH/JDK25.0.4）、2026-10-20/dev-foundation/上記source。1524/1525の当工具scopeは完了、本保存commit。1523/1283は実PG/独立再試験前でOPEN。次は元6014真正0→独立6016/原XML/counters/当630joinを先に保全し、二source当六Errorの同値PG可否を既独立Test/実四counterから確定。Main変更はそれまで0。global/F03/native/CHR/451/trace/QA051final/正式1964-53・実VM安全不明HOLDは未完、通常区切り停止0。
