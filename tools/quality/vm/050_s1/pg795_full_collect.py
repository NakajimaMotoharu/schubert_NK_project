"""Independent3517/520/1620 same-run six-module qualification; no old native import."""
from pathlib import Path
from pg714_full_collect import source as prior
from pg662_sources import replace

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')


def source():
    return replace(prior(),(
        ('pg713-expiry-six-host-v1','pg794-completion-six-host-v1'),
        ('pg712-expiry-core-qualification-v1','pg791-completion-selected-v1'),
        ('6ec88744cd5bffc3eee238753cba6bf22e21b8f4dd96287852de0c9121d804ef','34e9bdbd40748e70ecafcafb46c076b3bc12e5fdf668b4287250ce173e998807'),
        ('3502, 283, None','3517, 289, None'),
        ("sha(selected/'manifest.safe.json')", "sha(selected/'run.safe.json')"),
        ("reference = W/'pg711-expiry-core-v1/batch'/name if module == selected_module else old/module/name", "reference = selected/'batch'/name if module == selected_module else old/module/name"),
        ("json.loads((selected/'manifest.safe.json').read_bytes())['jarSha256']", "json.loads((W/'pg793-selected-qualification-v1.safe.json').read_bytes())['jarSha256']"),
        ("old = W/('pg680-owner-six-host-v1'if selector=='PG630'", "old = W/('pg748-closing-six-host-v1'if selector=='PG630'"),
        ('b710c69b798fcd14b35644541aed835689d81e6f0cbf40c3d67786e014f599e6','d4d3ba09651c75d15334e2775fa9a1ae8f8362e2fa92d9e8ebb57c1d8667d96e'),
        ('suites == 517 and total_classes == 1614','suites == 520 and total_classes == 1620'),
        ("'9bd50536f692610036a0ed8b83e0a8b35fe2a66f'if selector=='PG630'", "'8d4b68b4f1449932ebe506aaf08e584bbfea8dd2'if selector=='PG630'"),
        ("assert sha(selected/'run.safe.json') == selected_sha", "assert sha(selected/'run.safe.json') == selected_sha\n    assert sha(W/'pg793-selected-qualification-v1.safe.json')=='384ce98b2fac71452f178f76eb3112e148566867fa7dfb9b8508a68e2a69284a'"),
    ))


if __name__=='__main__':
    env={'__file__':str(R/'pg795_full_collect.py'),'__name__':'independent_completion_six'}
    exec(compile(source(),'<fixed794 six source qualification>','exec'),env)
    recorded=(W/'pg794-completion-six-host-v1/source').read_text().strip();env['main'](recorded,'PG630')
