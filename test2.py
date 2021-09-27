import unittest

if __name__ == "__main__":
    print(unittest.main(module='test', verbosity=2, exit=False).result.failures)