# WD-BUG-007 (副担当ローカル、正式915採番待ち)

User詳細の操作formにもsummary anchor、control id/for、必須の可視表示がない。UI222§5/SS313§10/225§5から4操作の固定id、Role/password/confirmの必須表示とnative requiredを補う。複数form間でidを重複させない。hidden ID/version/token/operation/状態は操作formにまとめたanchorを使う。self保護/Lock判定/最後ADMINは主担当controller/serviceが所有し変更しない。許可JS3本の外に必要な操作後client-disabledは未達として引継ぐ。
