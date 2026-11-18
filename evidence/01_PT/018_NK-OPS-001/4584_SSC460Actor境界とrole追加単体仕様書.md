# SSC-460 Actor境界とroleの補充試験

BUG-3232、SS314 §6/9、SS331、UI226、PT-AUT-ACTORVALUE003。独立期待はN12範囲1..999999999999、username 1..64 UTF-8 byteとnonnull role。新テストはID 0／1000000000000、空username、null username／roleを独立エラーとして確認する。Role公開名は USER, ADMIN のみ。配列変更が次の取得へ伝播せず、named lookupは大文字が正規で小文字を拒否することを確認。既在庫16の期待を維持し、同じProduct Coreで全17を一回実行。初回の16成功と実測coverage不足を保存し、異なるテストsourceのexec合算0。
