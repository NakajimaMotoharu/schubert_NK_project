"""Only actual PG725 current55ac proof; unchanged genuine ordered TERM protocol."""
from pathlib import Path
from pg724_retention_sources import bind
from pg662_sources import replace

R=Path(__file__).resolve().parent


def source():
    return replace(bind((R/'pg696_stop_binding.py').read_text()), (
        ('pg696','pg728'),('Pg696','Pg728'),('PG696','PG728'),('PG682','PG715'),
        ('8633b77f-77dc-4a78-88b4-41165f159b43','55ac70e7-0180-4c32-8c91-5a379ebedf24'),
        ('2026-10-09T00:43:10.150245Z','2026-10-09T03:00:51.014287Z'),
        ('2026-10-09T00:43:10.150245+00:00','2026-10-09T03:00:51.014287+00:00'),
        ('121088459330','129349297774'),
        ('pg693-completed-readonly-v1','pg725-completed-readonly-v1'),
        ('pg685-completed-activate-v1','pg717-completed-activate-v1'),
        ("('ad15ac4a-8d8e-4970-bcb3-2e000050ce77',", "('c6815985-26c5-4f5f-aed0-abc81fa8f71e','ad15ac4a-8d8e-4970-bcb3-2e000050ce77',"),
    ))


def namespace():
    env={'__file__':str(R/'pg728_stop_binding.py'),'__name__':'current_genuine_owned_stop_binding'}
    exec(compile(source(),'<current actual proof bindings>','exec'),env)
    return env


def generate(proof):return namespace()['generate'](proof)
def bindings(proof):return namespace()['bindings'](proof)
