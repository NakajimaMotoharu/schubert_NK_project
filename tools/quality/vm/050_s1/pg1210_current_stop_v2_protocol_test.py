"""Run all qualified control/actual writer fault vectors against current v2."""
import inspect
import unittest
import pg1202_current_stop_protocol_test as previous


def source():
    s=inspect.getsource(previous).replace('from pg1198_current_stop_binding import generate','from pg1208_current_stop_v2_binding import generate').replace('from pg1198_current_stop_binding_test import fixture','from pg1208_current_stop_v2_binding_test import fixture')
    s=s.replace('pg1198_durable','pg1208_durable').replace('pg1198_native_owned_stop','pg1208_native_owned_stop')
    return s


if __name__=='__main__':
    env={'__name__':'qualified_v2_protocol','__file__':__file__}
    exec(compile(source(),'<v2 independent fixed protocol>','exec'),env)
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(env['CurrentProtocolTest'])
    result=unittest.TextTestRunner().run(suite)
    if result.testsRun!=3 or result.skipped or not result.wasSuccessful():raise SystemExit(1)
