import inspect
import unittest
import pg1202_current_stop_protocol_test as previous


if __name__=='__main__':
    s=inspect.getsource(previous).replace('from pg1198_current_stop_binding import generate','from pg1216_current_full32_stop_binding import generate').replace('from pg1198_current_stop_binding_test import fixture','from pg1216_current_full32_stop_binding_test import fixture')
    s=s.replace('pg1198_durable','pg1216_durable').replace('pg1198_native_owned_stop','pg1216_native_owned_stop')
    env={'__name__':'qualified_full32_protocol','__file__':__file__};exec(compile(s,'<actual full32 stop protocol>','exec'),env)
    result=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromTestCase(env['CurrentProtocolTest']))
    if result.testsRun!=3 or result.skipped or not result.wasSuccessful():raise SystemExit(1)
