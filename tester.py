import unittest, json
class Tester(unittest.TestCase):
    def setUp(self) -> None:
        with open("testing/log/testlog.txt", "r") as test_log:
            self.tests = test_log.readlines()
            
    def add_test(self, function, excepted, input_parameters) -> None:
        test = {
            "function" : function,
            "expected" : excepted,
            "result" : None
        }
        for arg_name in input_parameters.keys():
            test[arg_name] = input_parameters[arg_name]
        with open("testing/log/testlog.txt", "a") as test_log:
            test_log.write(json.dumps(test))
            
    def run_tests(self) -> None:
        if len(self.tests) == 0:
            print("Has not setup yet")
            return None
        for test in self.tests():
            pass
test = Tester()