# 2557 Batch transaction例外順位28raw 静的点検仕様

訂正（BUG2085/YKT1833、原記述保全）：下の「4catch」とevent2942の同説明は二sourceの全catch数を混同した。原XMLの警告包含catchは各inner cleanupFailure一つ、計2。raw28/14operand/全期待順位・予算は不変更、14020失敗は保持し新14021/22で二anchorと反例を確認する。

2026-10-29/PG-D844/event2942、source0061/HEAD2c7516fa0、WBS-F03のみ、開始0.5/2/4pp cap10を固定。P01705/07は原artifact参照追加0。製品PT予定0・実DB/Backup/Root/VM/native/原本/鍵/回収/退役/permit/intent等0、source/SS/元静的XMLだけ。

BackupCommitService.complete PMD02703～02714（12raw/6span）、StepCleanupService.transaction PMD02756～02771（16raw/8span）、計28raw/14型operand/4catch。原XMLのmultiplicity2/ordinal/rowhashを保持し、SS341§6.6 BUG193/YKT152の未知primary同identity＋固定secondary、既知primary＋未知cleanup優先、known/unknown Runtimeの区分を照合する。SQL/Repository/停止理由を一般Runtimeと混同せず、Step committed=true後のrollback0・Connection破棄義務も確認する。

whole Main二sourceと固定例外/MutationGuardを読取。1364は旧sourceのレビューとして非改変保全し、当sourceの実測やPT成功へ転用しない。現source正常compile13832/承認origin-main SS331341/485canonical owner/元XMLに束縛し、14020と独立14022の型/offset/重複/順序反例を2558へ保存する。期待値は承認SS/固定category表と原XML、Product実行でexpected生成0。

反例・モデルはmetadata/source文字列だけで、実Throwable graph/DB/JMS操作をしない。raw警告・全whole pending・未測定を保持、Main変更やPT/PASS/coverage/native/正式受入へ換算0。参照のWBS合流は後続群と一度に行い、未合流分を現ref件数へ先行加算しない。これは品質確認の省略ではなく管理差分の集約。
