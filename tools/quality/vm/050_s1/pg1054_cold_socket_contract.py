"""SSC245 Linux little-endian /proc TCP endpoint codec, independent from DB/display.

Closed loopback read-only recovery scope only; no sockets are opened or changed.
"""
import ipaddress
import re


def endpoint(net, value):
    if net not in ('tcp', 'tcp6') or type(value) is not str:
        raise ValueError('kernel endpoint type refused')
    length = 8 if net == 'tcp' else 32
    if re.fullmatch('[0-9A-F]{' + str(length) + '}:[0-9A-F]{4}', value) is None:
        raise ValueError('kernel endpoint schema refused')
    encoded, port = value.split(':')
    raw = bytes.fromhex(encoded)
    if net == 'tcp':
        address = ipaddress.IPv4Address(raw[::-1])
    else:
        address = ipaddress.IPv6Address(b''.join(raw[i:i+4][::-1] for i in range(0, 16, 4)))
        if address.ipv4_mapped is not None:
            address = address.ipv4_mapped
    return str(address), int(port, 16)


def match(net, local, remote, state, client_host, client_port, server_port):
    if (client_host not in ('127.0.0.1', '::1') or type(state) is not str
            or any(type(p) is not int or not 1 <= p <= 65535 for p in (client_port, server_port))):
        raise ValueError('fixed client identity refused')
    own = endpoint(net, local)
    target = endpoint(net, remote)
    return own == (client_host, client_port) and target == (client_host, server_port) and state == '01'
