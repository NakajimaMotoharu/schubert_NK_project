# Scenario query boundary exploratory failures

`PT-SCN-20260908-explore04`: FieldCodec5成功、Scenario11件中failure1/error2。正式合格へ算入しない。BUG-030の整数読込変更後、Game/SQL通常読込は進行。

- BUG-031/YKT-028: capacity throwとTWR close SQLExceptionを重ねると元9001にsuppressed SQLが付く。resource scope外で固定例外へ再構築し、close不明時9000。検索・共通一覧の両方に複合故障testを適用する。
- BUG-032/YKT-029: UI223のtrim処理より先に元requestをwire検査していた。本文/話者/章をNFC/trimし、正規化requestを検査する。受信codecやCurrent baselineは変更しない。
- BUG-033: 最大pageのcountだけを模擬しrecordを4件のままにした不正fixture。正しいProtocol相関検査を緩めず、100entryを事前造成し正当な最大境界へ修正する。

探索02/03は選択testによりProtocolの必須test数が0となってbuild停止し、Scenarioを未実施。POMの必須checkを緩めず、探索04では選択にFieldCodecTestを含めた。正式runは無選択root clean verifyで全件実行する。
