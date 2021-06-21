import unittest


class ToolTestCase1(unittest.TestCase):
    def test(self):
        print("hello world")
        assert True


if __name__ == '__main__':
    unittest.main()
