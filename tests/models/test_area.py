from unittest import TestCase

from models.Area import Area, TileType


class TestArea(TestCase):
    def test_find_largest_empty(self):
        tiles = [[1, 1, 1, 1, 1],
                 [1, 0, 1, 0, 1],
                 [1, 0, 1, 0, 1],
                 [1, 1, 1, 0, 1],
                 [1, 1, 1, 1, 1]]
        tiles = [[TileType(x) for x in row] for row in tiles]
        expected = [[1, 1, 1, 1, 1],
                    [1, 1, 1, 0, 1],
                    [1, 1, 1, 0, 1],
                    [1, 1, 1, 0, 1],
                    [1, 1, 1, 1, 1]]
        expected = [[TileType(x) for x in row] for row in expected]
        actual = Area(5).find_largest_empty(tiles)
        self.assertEqual(expected, actual)

    def test_most_distant_tiles(self):
        tiles = [[1, 1, 1, 1, 1],
                 [1, 1, 1, 0, 1],
                 [1, 1, 1, 0, 1],
                 [1, 1, 1, 0, 1],
                 [1, 1, 1, 1, 1]]
        expected = ((1, 3), (3, 3))
        actual = Area(5).most_distant_tiles(tiles)
        self.assertEqual(expected, actual)

    def test_populate_tiles(self):
        tiles = [[1, 1, 1, 1, 1],
                 [1, 1, 1, 0, 1],
                 [1, 1, 1, 0, 1],
                 [1, 1, 1, 0, 1],
                 [1, 1, 1, 1, 1]]
        expected = [[1, 1, 1, 1, 1],
                    [1, 1, 1, 2, 1],
                    [1, 1, 1, 0, 1],
                    [1, 1, 1, 3, 1],
                    [1, 1, 1, 1, 1]]
        Area(5).populate_tiles(tiles)
        self.assertEqual(expected, tiles)

    @staticmethod
    def pretty_print(tiles):
        for row in tiles:
            for tile in row:
                print(tile, end='')
            print()
        print()
