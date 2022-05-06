import unittest
from misc.constants import testMargin

# from unit_test.testExample import TestExample
from unit_test.testBalloonSizing import TestBalloonSizing
from unit_test.testEnergyRequired import TestEnergyRequired
from unit_test.testFuelMassEstimation import TestFuelMassEstimation
from unit_test.testFuselageSizing import TestFuselageSizing
from unit_test.testInitializeParameters import initializeParameters
from unit_test.testISA import TestISA
from unit_test.testWingSizing import TestWingSizing


def main():
    """Main function for running unit tests"""
    unittest.main()


if __name__ == "__main__":
    main()

# Run the followign two commands in order to generate a code coverage report.
# coverage run -m unittest discover
# coverage report
