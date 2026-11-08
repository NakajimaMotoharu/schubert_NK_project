# NK-OPS-001 WBS現Source構造viewと履歴分離 製造確認仕様

BUG2517/YKT2255、G13.07主/G04関連追加0、REWORK原1/4/8pp cap10。旧inventory.source7fff/1061平面row、candidate e7d/943row、現7aed既22122/22126の1068静的descriptorを区別する。現1059共通/9新（C07監視template8・P02001 CHR validator1）/2旧配置を既metadataとGit filenameだけで照合。Source識別1068自体を再計算せず、Source/Test/compiler/JVM/原Root/cohort/native/VM/privatearchive/DB/credential操作を追加しない。

既descriptor baseを参照するversioned現構造viewを485へ、現owner/kindだけ既485正本からoverrideし新9は既資料のC07/P02001へ対応。旧1061一覧/311historicalSHA差・旧Source/candidate/予算/受入/全履歴は不変更保存。481へ現Source責務projectionを別追加（元190定義/旧1061projectionを維持）、486は参照hashを同保存単位で再束縛。全1068pathはGit filename set・owner有効/責務主担当・Source静的資格/実行資格非転用を確認。5CHRは静的domainを分離し過去component実行/nativeを移植しない。

既wbs_progress_auditのgraph/cost/個別exit metadataを維持し、現構造照合と未資格runtimeを分離。限定--current-source-structure-onlyだけ構造PASS可、通常全監査は現Sourceと旧candidateの未再認証で明示HOLD/nonzeroを維持し、未実施下流checkをPASSにしない。private runtimeの既計測検証やSource切替/再実行を呼ばない。新CLIは純metadata回帰（欠落/重複/別Source/owner不明/旧資格移植/fullHOLD偽PASS/履歴改変/参照不整合）で独立確認する。既oldSource runtime checkを迂回して全体PASSする変更は禁止。

着手前653pin/before24158保存、意味ある工具/文書/台帳commit/push。quality100%や新PTへ加点0、正式1964PT53scope/unique517/候補114/pending12/whole93/newleaf0/工数null/G07未分類3313+22/全HOLD・原本・七stash・Currentbaselineを保全。結果3854へ実command/exit・Source/manifesthash・未確定と次commandを記録し、通常区切りで停止しない。
