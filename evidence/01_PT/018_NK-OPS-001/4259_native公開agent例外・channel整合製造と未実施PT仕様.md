# native公開agent例外・channel整合製造と未実施PT仕様

NK-OPS-001 / WBS-P018-08.01/.02/.03 / BUG-2803/2804 / YKT2359/2399 / SS333342343352354451。FixedNativeCoverageCheckpoint.PublicAgentの3既知provider catalogでfatalgraphを固定診断前に確認。純profile parse IAE、固定agent/version/session/公開method/getExecutionData(false)、試行消費/new-only/Rootとnamespaceは不変更。

NativeCoveragePrivateFileはwrite初期位置0、正数count==buffer進捗、channel位置==buffer位置、force後の終端位置を検査する。hashは初期0、read正数==buffer位置・宣言残以内・channel累計、EOF正確-1/未消費buffer無しを検査する。正常FileChannel partial IO/byte/SHA256、原inode/metadata/force/close/sync/reopen、TWR例外優先は不変更。無進捗正数・count不一致・異常EOF/位置など13独立negative vectorをPG29112へSPEC_ONLYとして保存した。固定literal状態から期待を定義し、production methodでexpectedを生成していない。

原2Main全byte逆変換とGJF/CS0のみ確認。Main compile/NullAway/PMD/SpotBugs/wholePT/coverage未実施、13vectorは実行試験やcoverageではない。元wholeTestの全閉包・許可・資源後条件が成立するまで保留し、部分抽出/Root能力代替/実私有証跡を使う試行を行わない。実agent/native採取/Root/FD/privatefile/VM操作0、BUG2803/2804はOPEN。正式451/190の受入を増やさない。
