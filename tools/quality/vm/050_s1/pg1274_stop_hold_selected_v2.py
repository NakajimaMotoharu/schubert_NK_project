"""New-only seven actual shutdown PT; previous six and gap refusal preserved."""
import inspect
import pg1272_stop_hold_selected as previous


def main():
    source=inspect.getsource(previous.main).replace("changes==[TEST]", "set(changes)=={TEST,'src/schubert-nk-bootstrap/src/test/java/dev/codex/schubert/nk/bootstrap/FixedNativeCoverageRemovalDuringShutdownProbe.java'}")
    source=source.replace('pg1272-stop-hold-selected-v1','pg1274-stop-hold-selected-v2').replace("'tests':6","'tests':7").replace("'changedTestOnly':[TEST]","'changedTestOnly':changes")
    env=dict(previous.__dict__)
    exec(compile(source,'<new-only seven actual shutdown fixture>', 'exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
