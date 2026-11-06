# 487 writer 現cost版・列挙検証仕様

WBS-K03.02/BUG2356/YKT2101、source pmo_quota_binding +既pg998_metrics。管理metadataの19 unittest＝fresh観測/保存writerの旧14＋canonical writer005..009。Product PT/counterへの算入0。事前登録600022、原.25/.75/2 cap3、既S/V及び各元group見積/共有区間を不変とする。

TempDir台帳/receiptだけを使用し、現v2cost版と484自己revision/hashを結合。unknown revision/category/type、親leaf、不正/旧receipt/重複/時刻改竄/limit10以下を拒否、GROUP_ENDは既規定CHECKPOINT+END、詳細分類はworkDetailCategoryへ分離、原開始見積をそのまま保持する。Canonical writer testsではPath.open sentinelがlive台帳へのアクセス自体を拒否、Git照会はfixtureで差替え。VM/サービス/DB/Production操作0。

実commandはPG20822 metadata-begin.safe.json：PYTHONPATH=tools/quality:tools/quality/vm/050_s1、python3 -B -m unittest discover -s tools/quality/tests -p test_pmo_quota_binding*.py -v。moduleは所定vm/050_s1に存在し、folder名をVM実行許可とは扱わない。Source固定後19case/actualexit0/FES0を独立20826へ結合。旧WIP18は最終revision/IO guard追加前の履歴として別記し、新件数に加算しない。

4040～4051の12rowはrawを一切変更せず型/分類projectionだけを追加。4042/43のmetadata cost分類、4044/45のUnit親→leafは未確定のまま空canonical leafと原参照を残す。元source/日時/見積/観測区間/実結果を保持、旧時代の未登録type298/category316は生成当時のschema適用性を未判定とし自動再分類・受入へ変換しない。
