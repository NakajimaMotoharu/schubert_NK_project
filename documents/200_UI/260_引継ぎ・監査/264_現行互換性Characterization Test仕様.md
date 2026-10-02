# 現行互換性Characterization Test仕様

## 1. 目的・状態

現行schubertを利用者向け挙動のbaselineとし、schubert NKの画面design、遷移、検索結果・順、page、media操作、主要errorを
同じtestで比較する。意図的差異は本書の差異一覧だけを許容し、未登録差異は不具合とする。

関連RD: SCP-001、SCP-004、TST-001～TST-005、TST-103、MIG-002、MIG-006。
関連QA/RDF/UIC: QA-044、RDFなし、UIC-004。

本書のtest case設計と静的baselineはUI工程で作成済み。実行可能test artifactと現行実行baselineは、2026-09-01にNK production codeから分離した`program/characterization`として作成・実行済みである。Current適用23 caseは全PASS、CHR-N01 metadataはPASS、同一条件の2回目は差分0であり、production PG開始gateを合格した。

## 2. 現行baseline識別

2026-08-31に次をread-onlyで確認した。

| 対象 | Root | File数/集約SHA-256 |
|---|---|---|
| Current source・schema | `/home/mini/codex/project1/schubert_project/program/app/src`、`program/database` | Source 56＋DB関連3件。`c9ce7c85de2d0443b4d7bb4d9a3082b39985c1cbf3121945de1ee4a936b0bd6c` |
| Current document | `/home/mini/codex/project1/schubert_project/documents` | Markdown 18件。`1904756ba0e0cbf73f3942ad8481d17d727e3e8f3770dacf8bc64ee06c2acaff` |
| Master data | `/home/mini/codex/project1/schubert_project/data/master` | 59,627 file、19,240,707,190 byte |
| Scenario基準 | Current PostgreSQL/schema資料 | 262 file、99,661 entry、audio metadata 37,256、link 35,201 |
| Media基準 | Current source/file | Video 20、Music 129 |

集約hashはrootからの相対path順に各fileのSHA-256を列挙し、その列挙byte列をSHA-256化した値である。Characterization実行前に
再計算し、不一致ならbaseline変更理由を差異管理して本書とtest artifactを同時更新する。

## 3. Test artifact・証跡

NK repository内へ次を作成し、現行で全case成功後にbaseline commitを付ける。2026-09-01に実行済みである。

```text
program/characterization/
  tests/                 # 同一caseをcurrent/NK base URLへ実行
  fixtures/              # account名以外の秘密を含めない入力
  baseline/current/      # 正規化JSON、HTTP header、DOM snapshot、必要画面PNG
  reports/               # 実行version、日時、case結果、差異ID
```

- Testはbase URL、USER/ADMIN credential、asset rootを外部設定し、credentialをGitへ保存しない。
- HTMLはCSRF/session等の可変値を除外してsemantic DOMを比較し、主要画面はviewportを固定してscreenshotも比較する。
- DB内部ID、class、SQL、storage pathは比較しない。表示順はlogical contentとdisplay pathの列で比較する。
- HTTPはmethod、status、redirect、Content-Type/Disposition/Length/Rangeを比較する。
- Current成功baseline、source集約hash、本書version、実行環境を同一commitへ固定する。
- STは同じartifactをNKへ再実行し、差異IDに紐付く期待値だけをNK側oracleとして許容する。

## 4. Characterization case

| Case | 対象 | Current baseline・比較内容 | 証跡 |
|---|---|---|---|
| CHR-A01 | Login表示 | Username autofocus/autocomplete、password autocomplete、CSRF、error/lock/logout message、password非再表示 | DOM/header |
| CHR-A02 | Login制御 | User 5回、IP 10回、15分lock、成功clear。現行は設定と異なり3 sessionとも継続（DIF-016）、NKは最大2 session・最古失効 | HTTP/監査結果 |
| CHR-A03 | Logout・期限 | POST logout、302、期限切れGET/POST、保存済みsafe GET復帰 | HTTP遷移 |
| CHR-U01 | Menu | 2列card、現行の業務4機能＋Log照会の5 cardのtitle/順、top bar、responsive 1列 | DOM/PNG |
| CHR-U02 | 共通style | 色、幅、見出し、nav、focus、0件、error表示 | DOM/PNG |
| CHR-S01 | 検索条件 | 本文/game/speaker/章/type/voiceの単独・AND、trim、大文字小文字 | 正規化結果 |
| CHR-S02 | Speaker候補 | Game変更、出現数降順、同数名前昇順、JavaScript無効時submit | DOM/結果 |
| CHR-S03 | 検索順・page | Current entry順、100件/page、0以下を1、超過を最終page、範囲表示 | ID非依存結果 |
| CHR-S04 | 検索0件 | 空結果文言、前後page controlなし | DOM |
| CHR-S05 | Game/Route | 2 game title/order、全prefixと`～ルート`表示、未分類fallback | DOM/結果 |
| CHR-S06 | File一覧 | Current file順、章title→section code→file名fallback、display path、件数 | 正規化結果 |
| CHR-S07 | Scenario明細 | 前後file、entry順、anchor highlight、speaker/narration、本文 | DOM |
| CHR-S08 | Scenario audio | Audio有無、複数voiceのgroup化、inline player、DL file名 | DOM/HTTP |
| CHR-M01 | Audio HTTP | Inline/downloadのstatus、MIME、disposition、404 | HTTP header/body長 |
| CHR-M02 | Animation menu/list | Main 11＋SUBTRACK 4の15、OVA 4、opening 1、223の20 ID/title/path/order/pair | DOM/manifest |
| CHR-M03 | Animation watch | Opening/各ID直リンク、title/category/display path、戻り先、16:9 player | DOM/PNG |
| CHR-M04 | Video Range | 200、206、最初のRange、1MiB上限、suffix、416、Content-Range | HTTP header/hash |
| CHR-M05 | Music階層 | Category `曲`→`BGM`、section順、129件、非`曲`path/MB表示 | DOM/manifest |
| CHR-M06 | Music pair | 正規化key、完全一致、距離2以下、順序、Main/Inst欠落placeholder | 正規化pair一覧 |
| CHR-M07 | Music HTTP | Inlineの実MIME、download octet-stream、UTF-8名、Range/416 | HTTP header/hash |
| CHR-L01 | Log | Current filter、日時降順、100件/page、detail項目、0件、Web REQUESTのHTTP項目がWLGEVT01再送後も欠落・重複0 | 正規化結果/DOM/DB |
| CHR-E01 | Error | 401/403/404/409/416/503の文言、秘密/path/exception非表示 | HTTP/DOM |
| CHR-N01 | 新規機能 | USER/ADMIN menu差、User管理、質問/空回答/通知/取消/回答削除、更新token同一payload replay・異payload拒否 | NK受入結果 |
| CHR-O01 | Restart/cache | Session継続、no-store、Caddy/Web/MQ/API依存障害 | HTTP/運用log |

## 5. 正式差異一覧

| 差異ID | Current | NK | 理由・関連RD | 利用者影響 | 比較case | 状態 |
|---|---|---|---|---|---|---|
| DIF-001 | Brand `schubert` | `schubert NK` | 再構築識別、SYS-001 | Header/title変更。Login titleはCurrent `schubert - ログイン`→NK `schubert NK - ログイン`だけ | CHR-A01/U01/U02 | QA-045/UIC-005承認、SSC-074 |
| DIF-002 | 全利用者がLog閲覧 | ADMINだけ | AUT-002、FUN-008 | USER menuからLog消去 | CHR-L01 | RD確定 |
| DIF-003 | 現行4機能menu | 質問・通知・回答、ADMIN User管理追加 | FUN-009～013 | Card追加 | CHR-U01/N01 | RD確定 |
| DIF-004 | File account、Web内認証 | PostgreSQL account、MQ API認証、USER/ADMIN | FUN-001、AUT-001～004 | Account再作成、role表示 | CHR-A01～03 | RD確定 |
| DIF-005 | Spring標準error中心 | 共通styleと再操作案内 | TST-002、SYS-013 | Error文言統一 | CHR-E01 | UI設計決定 |
| DIF-006 | 多くの文字入力に明示上限なし | 固定長byte上限、定義外値拒否 | MQ-015～018、MSG-003～008 | 超過入力をfield error | CHR-S01/E01 | RD確定 |
| DIF-007 | 一部画面だけnav情報 | 全保護画面にusername/role/logout | AUT-002、SECURITY設計 | Top bar情報追加 | CHR-U02 | UI設計決定 |
| DIF-008 | 0件は空領域となる画面あり | `該当するデータはありません` | Accessibility、TST-002 | 空状態が明確 | CHR-S04/L01 | UI設計決定 |
| DIF-009 | 複数voice時に本文重複の可能性 | Entry単位group化し本文1回 | DAT-004、現行dataの将来整合 | 現行1 link dataでは差なし | CHR-S08 | UI設計決定 |
| DIF-010 | Log条件/levelが限定 | WARN、From/To、MQ/SYSTEM/BATCH等追加 | FUN-008、MON-003 | ADMIN検索項目追加 | CHR-L01 | RD確定 |
| DIF-011 | 認証済みHTML cache方針が限定的 | `Cache-Control: no-store` | SYS-013、MON-004 | Back時に再取得あり | CHR-O01 | UI設計決定 |
| DIF-012 | 無効Rangeの明示仕様なし | 416＋総長Content-Range | PER-004、TST-002 | 不正Range応答を標準化 | CHR-M04/M07 | UI設計決定 |
| DIF-013 | Inline onchange | CSP適合のsame-origin外部JS、無効時button | Security、TST-002 | 見える操作は維持 | CHR-S02 | UI設計決定 |
| DIF-014 | Web process内session | 暗号化永続session、再起動継続 | AVL-003、OPS-006 | 計画再起動後も継続可能 | CHR-O01 | UI設計決定 |
| DIF-015 | 現行URL | 受入条件外。ただし既存path継続 | TST-005 | 初期releaseで変更なし | 全HTTP case | RD確定 |
| DIF-016 | 同一accountの3件目Login後も3 sessionすべて利用可能 | 最大2 session、3件目で最古sessionをrevoke | 現行のsession lifecycle連携不備を既知不具合として修正、AUT-004、QA-044/UIC-004 | 3台目Login時に最古sessionがLogin画面へ戻る | CHR-A02 | 承認済み |

`UI設計決定`はRD範囲内の軽微な具体化であり、STで受入確認する。期待値変更または新たな利用者差異が判明した場合は、無断で
追加せずQA/RDFB適用要否を判定し、本表、test oracle、関連設計を同時更新する。

## 6. Gate・完了条件

| Gate | 条件 | 現在状態 |
|---|---|---|
| UI完了 | Case、差異、静的baseline、後続責務が確定 | 作成済み、263監査対象 |
| PG開始 | Executable artifact作成、current全case成功、baseline commit、差異review | 2026-09-01 PASS。CHR-G01～G06全件PASS、gate commit `843de94` |
| ST完了 | 同じartifactをNKへ実行し、登録差異以外一致、新規機能case合格 | 後続 |
| Release | 未承認差異0、重大未実施0、証跡version固定 | 後続 |

Current側の実行不能やsourceと実動の差（例: CSPとinline handler）を発見した場合は、実動結果をbaselineとし、NKで修正するなら
新しい差異IDと理由・影響を登録する。Source記述だけでbrowser挙動を推測して合格扱いにしない。

## 7. 更新履歴

| 日付 | 内容 |
|---|---|
| 2026-09-01 | QA-044/UIC-004の承認に基づき、現行の同時session上限不具合を`DIF-016`として登録し、CHR-A02のCurrent/NK oracleを分離。 |
| 2026-09-01 | Executable artifactでCurrentを2回実行し、適用23/23 PASS、catalog 24/24、2回差分0、DIF-001～016整合、秘密情報hit 0、CHR-G01～G06 PASSを確認しbaselineへ昇格。 |
