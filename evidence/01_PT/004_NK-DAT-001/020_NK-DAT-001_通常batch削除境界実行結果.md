# NK-DAT-001 通常batch削除境界実行結果

最新正式再試験: PT-WEB-20260909-33/sourcef3940eac、2026-09-09 16:11:26～16:18:10 JST、dev-foundation、exit0。全体995件（Protocol80/Storage42/API562/Web241/Batch29/CHR41）、6 Java moduleのline/method/class/branch100%・静的解析0。対象Test ID・個別結果・coverageはevidence/outbox-only-cleanup/manifest.json、SHA-256 `adec024b2030b0b17047c01fa73655ebb9cc33e3f8113adbd41cd71186d85842`。全29scope/9collectorの同一run/source/branch・全hash/参照、017の1件・019の7件負canary成功。Current baseline不変、秘密pattern scan0hit。更新対象binding codecは追加合格したが更新3参照/通常writer・replay/main・oneshot/親OS・実backup/実NK CHRは未完了。以下は個別試験の経緯・過去の探索履歴。

最新正式判定: PT-WEB-20260909-25/source6dd862d0、2026-09-09 12:46:41 JST完了、全918件PASS、failed/error/skipped0、5 Java moduleの4種coverage100%、静的解析0。本仕様8 PTも全PASS。evidence/outbox-only-cleanup/manifest.jsonの現行SHA-256は `f89c5b0bf4f001c41470fc03247c4b6661f68faa375e396bd3872c152516f1e9`。8collector/23scopeの全hashとtrace負canary、V001～013/Current baseline不変、秘密pattern scanを確認。本scopeのcoverage/SQL分岐対応は同manifestと以下の個別結果へ追跡。鍵file読取/main/oneshot・親process・Question/通知参照/親chunk走査は未完了、BUG-014/SSC-049継続。

以下は初回探索時の履歴。未確定という記述は本sliceだけ上記で更新済み。旧hashは証跡commit b84d81ef等の該当履歴を参照し、現行manifestと混同しない。

## 1. 判定

探索2: 追加8/旧Outbox4/既存DB15/旧SQL24/Protocol5/Storage16=72件PASS、failed/error/skipped0、静的解析0。正式全reactor・sanitized証跡未確定でありslice完了とは扱わない。QA-046/SSC-049、PG-D-126、BUG-014/YKT-012、019/PT065～072に対応。V011で通常batchの未検査Inbox削除を除去するが、全run/oneshot/7未対応参照/全cleanup横断監査が残るため障害全体は閉じない。

## 2. SQL条件・例外の網羅

| 条件 | Test ID / 独立後条件 |
|---|---|
| run/cutoff/limitの各NULL、非有限±、limit0/1/1000/1001 | 066/067、合法値は次gate、不正22023/0更新。NULL/非有限を無限保持削除へ解釈しない |
| helper正常/55P03/55000 | 067～070。正常のみ削除、競合LOCK_BUSY/未backup BACKUP_GATEいずれも0/0/0 |
| 例外catch範囲 | 067、Web側triggerのP0001を伝播し先行API削除もrollback。cleanup固有理由へ誤変換せず、trigger解除後2削除 |
| backup run/JST日付/ended_at/5状態/欠落 | 067/068/070、同run・同日・両側SUCCESSのみ、その他データ不変 |
| 同一locked snapshot、待機中別backup追加 | 070。当該呼出しBACKUP_GATE、次TXで再取得後1削除。pg_blocking_pidsを観測して同期しsleep不使用 |
| API/Web SENT/PENDING/ERROR、7日strict±1µs | 066/旧MessageStoreCleanupTest、各1/4番だけ消失、他6件保持 |
| lease NULL/期限±1µs/同値 | 066、NULL/期限超過だけ削除、同値/未来保持 |
| 1～1000合計chunk、API→Web、SKIP LOCKED | 066/069、API先頭削除/rollback復元/残API→Web、行lock中の1件だけ保持、解放後再走削除 |
| RETURN 0/1/複数・反復/rollback/commit | 065～070/072、literal件数・別connectionの可視性・SQL行IDで照合 |
| 全Inbox非干渉 | 065、31route＋ZZZ×3state=96行、NULL/公開不正cipher/5種参照の全列projection前後一致、隣接Outboxだけ2削除。072は旧不正Inbox2行保持 |
| 現行function/直接DML/role・PUBLIC境界 | 071、6汎用cleanupはInbox非参照、Inbox DELETEを含む現行2関数は検査roleだけ。通常batchの直接Inbox/検査function/SET ROLEは42501 |
| owner/security/search_path/UTC | 071/DB-011。正確な設定配列だけ可。誤UTC/余分statement_timeoutのrollback-only改変を許容しない負canary |
| append-only/migration | 072/旧SQL24/DB15、11履歴・再適用0、独立固定V001～009 SHA＋V010 SHA不変 |

## 3. 障害・横展開

BUG-091/YKT-082は旧DB-011のproconfig比較がV011固定UTC追加を追跡しなかったoracle漏れ。旧5functionはsearch_pathだけ、新message_storesはsearch_path＋UTCのexact配列へ是正。部分一致へ緩和しない。旧認証候補/削除/全候補の3classは元からUTC込みexact値で非該当。全5classを同じV011上で再試験し、071に改変negativeを追加した。正式証跡待ちで未完了。

## 4. 証跡

正式run後のevidence/outbox-only-cleanup/manifest.json/results.xml/checksumsにsource/branch/日時/OS・JDK・DB・driver/command/exit/input・expected・actual/Test ID/BUG/SSC/各hashを確定する。SQLに架空のJaCoCo割合を付けない。Java全4種100%はroot gateへ追跡する。原本baseline・既存migration不変確認、secret pattern scan、全15＋本scopeの相対trace/hash確認後に確定。PG/PTのみ、実NK CHR/IT/ST未実施。
