import unittest

from unit_test.testExample import TestStringMethods
from unit_test.testWeights import TestWeights
from unit_test.testSizing import TestSizing
from unit_test.testFuselage import TestFuselage
from unit_test.testState import TestState
from unit_test.testMisc import TestMisc
from unit_test.testFuelTank import TestFuelTank
from unit_test.testWing import TestWing
from unit_test.testDrag import TestDrag


if __name__ == '__main__':
    unittest.main()


# Run the following two commands in order to generate a code coverage report.
# coverage run -m unittest discover
# coverage report
