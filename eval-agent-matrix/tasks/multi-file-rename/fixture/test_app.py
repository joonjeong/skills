import unittest
from app.repo import load_user
from app.api import get


class T(unittest.TestCase):
    def test_load(self):
        self.assertEqual(load_user(1)["name"], "ada")

    def test_api(self):
        self.assertEqual(get(2)["label"], "Linus")


if __name__ == "__main__":
    unittest.main()
