"""One new owned loopback SOCKS for current4856 real CHR, no guest business command."""
import inspect
import pg2882_network_chr_socks as old

SLOT = 'pg3480-outbox-chr-socks-v1'


def main():
    ns = {**old.__dict__, 'SLOT': SLOT}
    exec(compile(inspect.getsource(old.main), '<one new owned current4856 loopback SOCKS>', 'exec'), ns)
    return ns['main']()


if __name__ == '__main__':
    raise SystemExit(main())
