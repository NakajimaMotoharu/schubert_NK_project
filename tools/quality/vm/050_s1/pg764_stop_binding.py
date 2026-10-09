"""Current758 actual proof only; immutable newownedTERM graph, no oldparent stop."""
from pathlib import Path
from pg728_stop_binding import source as previous
from pg761_current_binding import bind

R=Path(__file__).resolve().parent


def source():
    raw=bind(previous())
    marker="activation not in ('c6815985-26c5-4f5f-aed0-abc81fa8f71e',"
    assert raw.count(marker)==1
    return raw.replace(marker,"activation not in ('ab8895ca-4fb1-440d-b174-bc9f1f27505a','c6815985-26c5-4f5f-aed0-abc81fa8f71e',")


def namespace():
    env={'__file__':str(R/'pg764_stop_binding.py'),'__name__':'current758_ownedstop'}
    exec(compile(source(),'<newcurrent ownedstop>','exec'),env);return env


def generate(proof):return namespace()['generate'](proof)
def bindings(proof):return namespace()['bindings'](proof)
