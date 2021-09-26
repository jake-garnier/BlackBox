import unittest


def lambda_handler(event, context):
    unittest.main(module='test', exit=False)