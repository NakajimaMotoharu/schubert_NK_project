# 2565 共通静的context工具 実装・自己試験仕様

2026-10-29/PG-D848/event2950/source0061、開始0.5/2/4pp cap10・WBS-F03工具費のみ。原契約の消化、新受入、Product PT、coverageとは分ける。次のMain同期未参照59へ適用するための限定共通化であり、性能試走や新製品fixtureではない。既存pmd span/host provenance/canonical ownerは非改変再利用し、pmd_context/contract_dispositionや個別10622/10810を新設定で書換えて元資格を壊さない。

static_context_reader_v1 はdata-only plan（公開output/record・二rule・明示source/hash/owner/原ID/手動理由/guard/順序・限定prefix/SS hash）だけを処理する。known normal入力・Source pathと承認SS以外の任意実行/読取指定を認めず、held/traversal/unknown pathをmetadata/content前に拒否する。原findingのattrsと全multiplicityを保存し、raw抑制/NOT_APPLICABLE/実行免除/新受入は生成しない。Source importは関連hashのみでruntime allowlistへしない。

static_context_post_v1 は別XML/元catalog/独立line位置・元source/owner/typed pending/直接importを照合する。前処理の失敗を無条件継続せず、別の新OUTだけへ出力する。postのpure位置/真偽契約を工具自己試験で確認し、初回実SourceのI/O統合postは次の未分類群で検証する。過去22/原PTの成功を移植・再演して工具の動作証明にしない。

PG14060はmem上のsynthetic Java文字列/PMD形dict・raw duplicate二件/JSON値/reader spyだけ。Java/製品test/class/VM/DB/FS fixture/鍵/Root/許可発行/回収操作0。独立固定座標、未知/boolean/null/欠落/重複/path/owner/順序/prefixの拒否を検証する。SourceNormalized expectedはhashlib/固定literalから作り、製品methodから生成しない。工具の正負件数は実ラベル集合から導出し、Product PT件数に加算0。

初回bind前は全新library/entryのpyflakesとsource guardを確認。失敗entry/libraryは凍結し上書きせず必要BUG/YKTを先行する。結果/command/退出/hashは2566・公開manifestへ記録、正式1964/53・17/190・工数null/QA051final・全actualHOLD/原本と二held工具は不変。
