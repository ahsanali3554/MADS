import unittest

from memory_manager import MemoryBlock, MemoryManager


class MemoryManagerTests(unittest.TestCase):
    def test_first_fit_splits_the_first_available_block(self):
        manager = MemoryManager(100)

        self.assertEqual(manager.allocate(30), 0)
        self.assertEqual(
            manager.memory,
            [MemoryBlock(0, 30, True), MemoryBlock(30, 70)],
        )

    def test_positioned_allocation_preserves_space_on_both_sides(self):
        manager = MemoryManager(100)

        self.assertEqual(manager.allocate(20, 40), 40)
        self.assertEqual(
            manager.memory,
            [
                MemoryBlock(0, 40),
                MemoryBlock(40, 20, True),
                MemoryBlock(60, 40),
            ],
        )

    def test_deallocation_merges_adjacent_free_blocks(self):
        manager = MemoryManager(100)
        manager.allocate(20)
        manager.allocate(30)

        self.assertTrue(manager.deallocate(0))
        self.assertTrue(manager.deallocate(20))
        self.assertEqual(manager.memory, [MemoryBlock(0, 100)])

    def test_invalid_or_oversized_allocations_are_rejected(self):
        manager = MemoryManager(50)

        with self.assertRaises(ValueError):
            manager.allocate(0)
        self.assertEqual(manager.allocate(60), -1)
        self.assertEqual(manager.allocate(10, 45), -1)


if __name__ == "__main__":
    unittest.main()
