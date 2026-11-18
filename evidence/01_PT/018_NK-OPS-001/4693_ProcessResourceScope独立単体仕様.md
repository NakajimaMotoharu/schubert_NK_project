# ProcessResourceScope 独立単体仕様

NK-OPS-001／WBS-F03/2-1、P018-04、OPS009、UI251、SS343 SSC063/308、451、PG-D-1185、BUG-3305、YKT-2664。対象は ProcessResourceScope の private constructor、acquire、use。旧 QUERYOWN001〜007 は当該試験設計と run を保持する。

| Test ID | 入力・期待値の独立根拠 |
|---|---|
| PT-OPS-SCOPEVALUE001 | 指定型の private noarg を呼び、固定 AssertionError と構築拒否を確認。Java の反射アクセス設定は終了時に元へ戻す。当型以外を対象にしない。 |
| PT-OPS-SCOPEVALUE002 | null の三port、null返却、取得時 IOException。取得前の不正条件では取得・body・close回数0。取得失敗の例外は元と同一。 |
| PT-OPS-SCOPEVALUE003 | 独立する外側と内側のメモリ値。同じ値の受渡しと release の内→外順、一回。正常 body→release、release単独失敗の同一性。 |
| PT-OPS-SCOPEVALUE004 | 手書きの5種body × 3種releaseの順位表を acquire/use に適用。既知scope失敗に未知cleanupが勝つ場合、InterruptedExceptionの割込を保持。その他compoundではbody本人と固定StopGateException一個、通知理由 COMMAND_FAILURE、原因なし。 |

試験は新しい一つのwhole class。既試験を抜き出さない。JDKのheap値と同じJUnit workerの割込だけを使用する。割込は各fixtureのfinallyで回収する。実プロセス、Unit、NSS、DB、ネイティブ、外部ファイル、保護型を起動しない。再送は本クラスの責務外。

PG39751～39762の閉包、静的、生counter、単一exec、独立XML／CRCと終了コードを保全する。旧source/runと現sourceの証跡を合算しない。既callerの実行と全451は別の受入条件。
