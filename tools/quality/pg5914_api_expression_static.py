"""Exact three API owners and independent all851/1666 raw static; no PT invocation."""
import inspect
import pg5906_storage30_static as previous

PREFIX = 'src/schubert-nk-api/src/main/java/dev/codex/schubert/nk/api/'
REWRITES = {
    'application/admin/UserCommandService.java': [
        ('public final class UserCommandService {', 'public final class UserCommandService {\n  private static final int MAXIMUM_USER_VERSION = 999_999_999;\n'),
        ('if (before.version() == 999_999_999)', 'if (before.version() == MAXIMUM_USER_VERSION)'),
        ('              case ENABLE, DISABLE ->\n                  s.setString(p++, next.enabled() ? LITERAL_ACTIVE : "DISABLED");', '              case ENABLE, DISABLE -> {\n                s.setString(p, next.enabled() ? LITERAL_ACTIVE : "DISABLED");\n                p++;\n              }'),
        ('              case PROMOTE, DEMOTE -> s.setString(p++, next.role().wireValue());', '              case PROMOTE, DEMOTE -> {\n                s.setString(p, next.role().wireValue());\n                p++;\n              }'),
        ('                s.setString(p++, next.hash().orElseThrow());', '                s.setString(p, next.hash().orElseThrow());\n                p++;'),
        ('                s.setObject(p++, metadata.at().atOffset(java.time.ZoneOffset.UTC));', '                s.setObject(p, metadata.at().atOffset(java.time.ZoneOffset.UTC));\n                p++;'),
        ('            s.setObject(p++, metadata.at().atOffset(java.time.ZoneOffset.UTC));', '            s.setObject(p, metadata.at().atOffset(java.time.ZoneOffset.UTC));\n            p++;'),
        ('            s.setLong(p++, actor.userId());', '            s.setLong(p, actor.userId());\n            p++;'),
        ('            s.setLong(p++, id.value());', '            s.setLong(p, id.value());\n            p++;')],
    'file/AssetChecksumManifest.java': [
        ('public final class AssetChecksumManifest {', "public final class AssetChecksumManifest {\n  private static final byte LINE_FEED = '\\n';\n"),
        ('      int read;\n      while ((read = channel.read(buffer)) != -1) {', '      while (true) {\n        int read = channel.read(buffer);\n        if (read == -1) break;'),
        ("if (value == '\\n')", 'if (value == LINE_FEED)'),
        ('            line[length++] = value;', '            line[length] = value;\n            length++;')],
    'idempotency/WipingByteArrayOutputStream.java': [
        ('    buf[count++] = (byte) value;', '    buf[count] = (byte) value;\n    count++;')]}
MODIFIED = {PREFIX + p for p in REWRITES}


def expected_source(path, before):
    for old, new in REWRITES[path.removeprefix(PREFIX)]:
        if before.count(old) != 1:
            raise ValueError('one exact declared API expression: ' + old)
        before = before.replace(old, new, 1)
    return before


def runner_source():
    raw = previous.runner_source()
    changes = {
        'pg5904-storage30-selected199-v1/manifest.safe.json': 'pg5912-api-expression-selected35-v1/manifest.safe.json',
        "(v['tests'],v['suites'])==(199,33)": "(v['tests'],v['suites'])==(35,10)",
        'pg5882-terminal-serial-static-v1/manifest.safe.json': 'pg5906-storage30-static-v1/manifest.safe.json',
        'provisional/PG5882-terminal-serial-static-v1/manifest.json': 'provisional/PG5906-storage30-static-v1/manifest.json',
        '2b5a42b051c804000affd8b92ea51c51c4e6dcf8e21addbed975a966335b7ec8': 'a0c4d80e21a1a20a05928d26a35168be6802aa01e2bc8a682bb6e49959ca5365',
        "expected_counts['AvoidLiteralsInIfCondition']-=9;expected_counts['AvoidSynchronizedStatement']-=21": "expected_counts['AvoidLiteralsInIfCondition']-=2;expected_counts['AssignmentInOperand']-=10",
        "'rawDiagnosticsRemovedByPg':30": "'rawDiagnosticsRemovedByPg':12",
        "before_snapshot=W/'pg5880-terminal-serial83-v1/source'": "before_snapshot=W/'pg5904-storage30-selected199-v1/source'",
        "provisional/PG5906-storage30-static-v1';target.mkdir()": "provisional/PG5914-api-expression-static-v1';target.mkdir()"}
    for old, new in changes.items():
        if raw.count(old) != 1:
            raise ValueError('one exact all851 API static binding: ' + old)
        raw = raw.replace(old, new, 1)
    compile(raw, '<all851 API static>', 'exec')
    return raw


def pg_contract(snapshot, value, old):
    # Reuse the original strict contract with a fully explicit function namespace.
    raw = inspect.getsource(previous.pg_contract).replace('pg5880-terminal-serial83-v1/source', 'pg5904-storage30-selected199-v1/source')
    scope = {**vars(previous), 'MODIFIED': MODIFIED, 'expected_source': expected_source}
    exec(compile(raw, '<three API owners strict contract>', 'exec'), scope)
    return scope['pg_contract'](snapshot, value, old)


def main():
    scope = {**vars(previous.engine), 'SLOT': 'pg5914-api-expression-static-v1', 'MODIFIED': MODIFIED, 'pg_contract': pg_contract}
    exec(compile(runner_source(), '<all851 API static>', 'exec'), scope)
    return scope['main']()


if __name__ == '__main__':
    raise SystemExit(main())
