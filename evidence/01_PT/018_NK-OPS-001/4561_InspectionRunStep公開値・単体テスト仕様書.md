# InspectionRun／InspectionStep公開値の単体テスト仕様書

P004-04、NK-OPS-001、UI251、SS341/351/451、BUG-3222/YKT-2673。P018-10.03 CATALOG016/017の通常値契約。旧PG18070/72の独立時刻、cursor、固定診断を参照し、元8ケースを変更せず、新試験4件を InspectionRunStepValueContractTest に登録する。

| Test ID | class/method | 範囲と独立期待値 |
|---|---|---|
| PT-P01810-CATALOG-016-time | InspectionRun constructor/id/cutoff/toString | 0001～9999年UTCの下上限を含むµs精度・中間3µs、範囲外直前直後と1nsを拒否、IDと日時null拒否。固定診断 |
| PT-P01810-CATALOG-016-key | InspectionRun equals/hashCode | 同じ固定値からの別instanceで固定Map値を取得。時間又はUUIDだけ異なるものは同じキーにならない |
| PT-P01810-CATALOG-017-state | InspectionStep constructor/outcome/cursor/toString | DELETED/PROTECTEDにはcursorが存在、ENDには存在しない、三値の反対の有無とnullは拒否。表示は固定Outcomeとcursor秘匿 |
| PT-P01810-CATALOG-017-key | InspectionStep equals/hashCode、Outcome | Outcome又はcursorだけ異なる場合のMap検索不成立、同値別instanceは成立。独立リテラルの順序、名前及び未知・null拒否 |

JDK25のUTC値・非機密の合成UUIDとHashMapだけを使用する。DB、原Inspector処理、並行Actor、外部再送、認証、nativeは外側の別試験。規範はSSの時刻・cursor状態・外部画面値を保持する。日時、Mapの文字列、三名称と診断の期待値を製品出力から生成しない。

同候補のMain 2ファイル／物理3 class、生成methodを含む17 Codeの独立coverageとCRC、JUnit XML、静的解析、終了codeを記録する。元coverageとの合算はない。command、環境、対象commitとhashは結果書と各run manifestを参照する。
