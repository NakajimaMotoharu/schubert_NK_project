import copy
import json
import unittest
import pg6948_c01_static_adapt as p


class C01StaticAdaptTest(unittest.TestCase):
    def fixture(self, address):
        listen = address if ':' not in address else '[' + address + ']'
        proxy = dict(handler='reverse_proxy', upstreams=[dict(dial='127.0.0.1:8080')],
          transport=dict(protocol='http', dial_timeout=2000000000, response_header_timeout=30000000000,
                         read_timeout=60000000000, write_timeout=60000000000),
          headers={'request': {'set': {'X-Forwarded-For': ['{http.request.remote.host}'],
            'X-Forwarded-Proto': ['{http.request.scheme}'], 'X-Forwarded-Host': ['{http.request.host}']}}})
        response = {'set': {'Strict-Transport-Security': ['max-age=31536000'],
          'X-Content-Type-Options': ['nosniff'], 'X-Frame-Options': ['DENY'], 'Referrer-Policy': ['same-origin']},
          'delete': ['Server']}
        handlers = [dict(handler='request_body', max_size=2000000), dict(handler='headers', response=response), proxy]
        server = dict(listen=[listen + ':55160'], automatic_https={'disable_redirects': True},
          routes=[{'handle': [{'handler': 'subroute', 'routes': [{'handle': handlers}]}]}])
        return {'admin': {'disabled': True}, 'apps': {'http': {'servers': {'owned': server}},
          'pki': {'certificate_authorities': {'local': {'install_trust': False}}},
          'tls': {'automation': {'policies': [{'issuers': [{'module': 'internal'}]}]}}}}

    def test_independent_ipv4_ipv6_semantics(self):
        for address in ('127.0.0.1', '2001:db8::1'):
            p.verify_json(self.fixture(address), address)
        self.assertEqual('a\nb', p.normal('# comment\n a\n\n b  \n'))

    def test_extra_handlers_or_wider_bind_and_body_limit_rejected(self):
        for mutate in (
          lambda x: x['apps']['http']['servers']['owned'].update(listen=[':55160']),
          lambda x: x['admin'].update(disabled=False),
          lambda x: x['apps']['pki']['certificate_authorities']['local'].update(install_trust=True),
          lambda x: x['apps']['http']['servers']['owned']['automatic_https'].update(disable_redirects=False),
          lambda x: x['apps'].update(extra={'handler': 'file_server'})):
            value = self.fixture('127.0.0.1')
            mutate(value)
            with self.assertRaises(ValueError):
                p.verify_json(value, '127.0.0.1')
        value = self.fixture('127.0.0.1')
        for node in p.walk(value):
            if node.get('handler') == 'request_body':
                node['max_size'] = 2097152
        with self.assertRaises(ValueError):
            p.verify_json(value, '127.0.0.1')

    def test_proxy_timeouts_client_trust_and_header_policy_not_relaxed(self):
        base = self.fixture('127.0.0.1')
        for change in ('timeout', 'upstream', 'trust', 'headers', 'forward', 'issuer'):
            value = copy.deepcopy(base)
            for node in p.walk(value):
                if node.get('handler') == 'reverse_proxy':
                    if change == 'timeout': node['transport']['dial_timeout'] = 0
                    if change == 'upstream': node['upstreams'] = [{'dial': '0.0.0.0:8080'}]
                    if change == 'trust': node['trusted_proxies'] = ['private_ranges']
                    if change == 'forward': node['headers']['request']['set'] = {}
                if change == 'headers' and node.get('handler') == 'headers': node['response']['delete'] = []
                if change == 'issuer' and node.get('module') == 'internal': node['module'] = 'acme'
            with self.assertRaises(ValueError):
                p.verify_json(value, '127.0.0.1')

    def test_vendor_tag_and_retained_ipv4_output_without_any_execution(self):
        # Official v2.6.2 pki.go json tag, not Go member CAs or a self-consistent alias.
        value = self.fixture('127.0.0.1')
        value['apps']['pki']['cas'] = value['apps']['pki'].pop('certificate_authorities')
        with self.assertRaises(KeyError):
            p.verify_json(value, '127.0.0.1')
        path = p.W / p.SLOT / '1.json'
        self.assertEqual('28f9a4df19349dc877a1a9765bdd3a4d6615fdb50633d68287b84531416395cf', p.sha(path))
        p.verify_json(json.loads(path.read_bytes()), '127.0.0.1')


if __name__ == '__main__':
    unittest.main()
