"""New-only qualified read collector retry; old empty failure slot retained."""
import inspect
import pg1288_physical_pin_counter as previous


def main():
    code=inspect.getsource(previous.main).replace('pg1288-physical-pin-counter-v1','pg1290-physical-pin-counter-v1')
    env=dict(previous.__dict__)
    exec(compile(code,'<new-only corrected component collection>', 'exec'),env)
    return env['main']()


if __name__=='__main__':raise SystemExit(main())
