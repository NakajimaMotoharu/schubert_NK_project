"""Independent fresh3513/519/1616 qualification with two changed selected JARs, no native import."""
import hashlib
from pathlib import Path
import subprocess
from pg714_full_collect import source as previous
from pg662_sources import replace

R=Path(__file__).resolve().parent
W=Path('/home/mini/codex/project1/work/pgpt-runs/PG379')


def source():
    selected=W/'pg745-closing-selected-v1/run.safe.json'
    assert selected.is_file()
    old="""reference = W/'pg711-expiry-core-v1/batch'/name if module == selected_module else old/module/name
        if module == selected_module:assert sha(reference)==json.loads((selected/'manifest.safe.json').read_bytes())['jarSha256']"""
    new="""reference = selected/module/name if module in ('bootstrap','api') else old/module/name
        if module in ('bootstrap','api'):assert sha(reference)==json.loads((selected/'run.safe.json').read_bytes())['files'][module+'/'+name]"""
    return replace(previous(),(
        ('pg713-expiry-six-host-v1','pg748-closing-six-host-v1'),
        ('pg712-expiry-core-qualification-v1','pg745-closing-selected-v1'),
        ('6ec88744cd5bffc3eee238753cba6bf22e21b8f4dd96287852de0c9121d804ef',hashlib.sha256(selected.read_bytes()).hexdigest()),
        ('3502, 283, None','3513, 289, None'),
        ("sha(selected/'manifest.safe.json')", "sha(selected/'run.safe.json')"),
        (old,new),
        ("old = W/('pg680-owner-six-host-v1'if selector=='PG630'", "old = W/('pg713-expiry-six-host-v1'if selector=='PG630'"),
        ('b710c69b798fcd14b35644541aed835689d81e6f0cbf40c3d67786e014f599e6','5f6a57015fb30d8f2097e594370d558ac6202a9d5d2ed98ce0108494cc7f524a'),
        ('suites == 517 and total_classes == 1614','suites == 519 and total_classes == 1616'),
        ("'9bd50536f692610036a0ed8b83e0a8b35fe2a66f'if selector=='PG630'","'1ec19782a1afe22d1de75b05f4cd12b8a8a8a172'if selector=='PG630'"),
        ("assert results['bootstrap']['tests'] == expected_bootstrap", "assert results['bootstrap']['tests'] == expected_bootstrap\n    assert results['api']['tests']==958"),
    ))


if __name__=='__main__':
    recorded=(W/'pg748-closing-six-host-v1/source').read_text().strip()
    assert not subprocess.check_output(['git','diff','--name-only','e24b246d5d83762650eda5574188d3b4f59fe501',recorded,'--','src','pom.xml'])
    env={'__file__':str(R/'pg748_full_collect.py'),'__name__':'closing_newsource_full'}
    exec(compile(source(),'<fresh six SSC234 newsource>', 'exec'),env);env['main'](recorded,'PG630')
