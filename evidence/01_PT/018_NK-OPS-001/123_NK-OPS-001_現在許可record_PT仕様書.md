# 現在起動許可record PT仕様書（PG302・実装前/未実行）

Program NK-OPS-001、予定Batch.file.StartupPermitRecords/Epoch/Permit/State、RD SYS-002/004・OPS009/UI251/SS341～343 SSC089、D03～05。canonical非秘密byte/valueだけの層で、原本inode/atomic更新、parent M/A/実工程証明、root issuerを代替しない。scope成功だけで現在permitを発行しない。

独立golden: boot `11111111-1111-1111-1111-111111111111`、epoch `33333333-3333-3333-3333-333333333333`、run `44444444-4444-4444-4444-444444444444`、activation `55555555-5555-5555-5555-555555555555`、cutoff `2026-09-27T00:00:00.000000Z`。Broker Invocation `22222222222222222222222222222222`、permit digest a×64、release b×64、API config c×64、Web config d×64、roots e×64、prestart steps f×64。全て公開fixtureで実起動許可ではない。SS343記載の順序・key・LFからliteral期待byteを試験側に直接作る。

| Test ID PT-OPS-PERMITREC | 入力/操作/独立期待値 |
|---|---|
| 001 | INVALID/ISSUED current・permit両goldenのliteral byte encode/parse、全member一致。実cutoff/activationを変更しない |
| 002 | 全missing/unknown/duplicate/順序違い/magic/末尾LF/CRLF/非ASCII/空/過大byte拒否、canonical byte一致を独立goldenで確認 |
| 003 | boot/epoch zero/UUID非canonical・短縮・uppercase、Broker0/不正文字・長、hash uppercase/63/65/不正char拒否 |
| 004 | state INVALID digestなし/ISSUED digestありだけ、逆組合せ拒否、再issuedを許可へ読み替えない |
| 005 | current ISSUEDとpermit実byte hash・boot/epoch/run/cutoff/activationの独立一致確認、各不一致/INVALID/旧permit拒否 |
| 006 | cutoff上下限/µs/非正規表示、既存BatchRunのtimestamp/null契約維持。新cutoffやdaily successを捏造しない |
| 007 | 全null/input collection/optional/redaction、不変snapshot、decodeでNPEをcatchし正常扱いしない |
| 008 | 並行独立encode/decode/issued照合、byteのcaller所有/非mutation、static/coverageの全分岐 |

事前条件はpublic synthetic valuesだけ。Execution/result/coverage/command/source commit/OS/tool/hash/関連BUGは実装後125以降へ記録予定（124はPG301回帰保存に使用）、現時点は全件not-runで合格0。初期TDD未実装REDを障害としないが、実装済処理のSS違反は915へ修正前登録する。現在epoch IO/真正原本/fullissuer/実morning/実NKは後続必須で別Test IDへ追加、全scope正式収集をclass追加ごとに反復しない。
