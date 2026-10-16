import unittest
from stats import moving_average, median


class T(unittest.TestCase):
    def test_ma(self):
        self.assertEqual(moving_average([1, 2, 3, 4], 2), [1.5, 2.5, 3.5])

    def test_ma_full(self):
        self.assertEqual(moving_average([2, 4], 2), [3.0])

    def test_median_odd(self):
        self.assertEqual(median([3, 1, 2]), 2)

    def test_median_even(self):
        self.assertEqual(median([4, 1, 3, 2]), 2.5)


if __name__ == "__main__":
    unittest.main()
