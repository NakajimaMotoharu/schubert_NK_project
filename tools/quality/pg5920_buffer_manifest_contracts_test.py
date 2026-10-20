import unittest
import pg5920_buffer_manifest_contracts as t


class ContractPremiseTest(unittest.TestCase):
    def test_actual_parent_shape_rejects_unsynchronized_copy_or_unexpected_signature(self):
        lines = ('void write(int);', 'void write(byte[], int, int);', 'void reset();', 'byte[] toByteArray();',
                 'int size();', 'java.lang.String toString();', 'void writeTo(java.io.OutputStream) throws java.io.IOException;')
        fixture = '\n'.join('public synchronized ' + s for s in lines)
        t.parent_contract(fixture)
        for line in lines:
            with self.assertRaises(ValueError):
                t.parent_contract(fixture.replace('public synchronized ' + line, 'public ' + line))

    def test_local_owner_rejects_public_or_escaping_or_unbounded_or_missing_wipe(self):
        fixture = ('class WipingByteArrayOutputStream extends ByteArrayOutputStream {\n'
                   'public synchronized a; public synchronized b; public synchronized c; public synchronized d;\n'
                   'private static final int MAXIMUM = 1_050_000;\n'
                   'Arrays.fill(old, (byte) 0); Arrays.fill(buf, (byte) 0); count = 0;\n'
                   'reserve(1);\n    buf[count] = (byte) value;\n    count++;')
        codec = ('private static byte[] compress(\nprivate static byte[] decompress(\n'
                 + 'try (var output = new WipingByteArrayOutputStream()) {\nreturn output.toByteArray();\n' * 2)
        fingerprint = ('  byte[] canonicalBytes(CanonicalRequest request) {\n'
                       'try (var output = new WipingByteArrayOutputStream()) {\nreturn output.toByteArray();\n'
                       'private static void writeText(ByteArrayOutputStream output,\n'
                       'private static void writeValue(ByteArrayOutputStream output,\n'
                       'private static void writeLength(ByteArrayOutputStream output,\n'
                       'Arrays.fill(canonical, (byte) 0);')
        t.buffer_contract(fixture, codec, fingerprint)
        for old, new in (('class Wiping', 'public class Wiping'), ('1_050_000', '2_000_000'),
                         ('Arrays.fill(old, (byte) 0);', ''), ('Arrays.fill(buf, (byte) 0);', ''), ('public synchronized a;', 'public a;')):
            with self.assertRaises(ValueError):
                t.buffer_contract(fixture.replace(old, new), codec, fingerprint)
        with self.assertRaises(ValueError):
            t.buffer_contract(fixture, codec.replace('return output.toByteArray();', 'return output;'), fingerprint)
        for old, new in (('  byte[] canonicalBytes', '  public byte[] canonicalBytes'),
                         ('return output.toByteArray();', 'return output;'),
                         ('private static void writeText', 'public static void writeText'),
                         ('Arrays.fill(canonical, (byte) 0);', '')):
            with self.assertRaises(ValueError):
                t.buffer_contract(fixture, codec, fingerprint.replace(old, new))

    def test_entire_reference_inventory_rejects_missing_or_new_unreviewed_scope(self):
        owners = {t.BUFFER: 3, t.CODEC: 2, t.FINGERPRINT: 1}
        t.reference_contract(owners)
        for changed in ({t.BUFFER: 2, t.CODEC: 2}, dict(owners, new_owner=1), dict(owners, **{t.FINGERPRINT: 2})):
            with self.assertRaises(ValueError):
                t.reference_contract(changed)

    def test_parser_rejects_mutable_publication_or_duplicate_acceptance(self):
        fixture = ('private final Map<String, String> hashes; this.hashes = Map.copyOf(hashes); '
                   'Map<String, String> hashes = new HashMap<>(); return new AssetChecksumManifest(hashes); '
                   'require(hashes.putIfAbsent(path, hash) == null);')
        t.map_contract(fixture)
        for old in ('Map.copyOf(hashes)', 'require(hashes.putIfAbsent(path, hash) == null);'):
            with self.assertRaises(ValueError):
                t.map_contract(fixture.replace(old, 'changed'))


if __name__ == '__main__':
    unittest.main()
