# F02 Storage追加辺の呼出順単体仕様

NK-PRO-003／NK-OPS-001、SYS-005、UI237、SS311／332／333のSSC-461、WBS-F02-a。対象は`StorageIoException.preserveFatal(Throwable, Function)`。呼出元が渡した追加辺を、既存のcauseと順序付きsuppressedの後ろに扱う。非Error未訪問のオブジェクトだけを一回評価する。SQL next変換のBootstrap試験とは独立。

| Test ID | 自己所有合成入力 | 独立期待値 |
|---|---|---|
| PT-OPS-STGRAPH-GENERIC-001 | root→cause、suppressed 2個、追加edgeの共有先と循環、追加edgeなし1個 | callback履歴の参照順はroot・cause・suppressed1・suppressed2・追加先の全5。各一回、終端、入力のcause／suppressed不変。 |
| PT-OPS-STGRAPH-GENERIC-002 | rootのcauseをLinkageError、suppressedを非Error、追加edgeを別AssertionErrorに固定 | 選ばれるのは先行causeの同一インスタンス。callbackはrootのみ。fatal自身と残りの未訪問項目は呼ばれず、入力の既辺を保存。 |

同一の現Storage包装から二物理を抽出し、新2と既6を同一runで実行する。正常・循環・null・Error・同depth優先、enumの公開契約を既期待と照合する。DB、file操作、対象外の実caller、旧公開一引数入口の削除は含めない。終了値、hash、JDKとcommandはmanifestに記録。
