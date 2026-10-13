"""Core memory-allocation model used by the desktop simulator."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MemoryBlock:
    start: int
    size: int
    allocated: bool = False

    @property
    def end(self) -> int:
        return self.start + self.size


class MemoryManager:
    """Manage a contiguous memory space using first-fit allocation."""

    def __init__(self, total_size: int):
        if total_size <= 0:
            raise ValueError("Total memory size must be greater than zero.")
        self.total_size = total_size
        self.memory = [MemoryBlock(0, total_size)]

    def allocate(self, size: int, position: int | None = None) -> int:
        if size <= 0:
            raise ValueError("Allocation size must be greater than zero.")

        if position is None:
            return self.first_fit(size)

        if position < 0 or position + size > self.total_size:
            return -1

        for index, block in enumerate(self.memory):
            if block.allocated or position < block.start or position + size > block.end:
                continue

            replacement: list[MemoryBlock] = []
            if position > block.start:
                replacement.append(MemoryBlock(block.start, position - block.start))
            replacement.append(MemoryBlock(position, size, True))
            if position + size < block.end:
                replacement.append(MemoryBlock(position + size, block.end - position - size))

            self.memory[index : index + 1] = replacement
            return position

        return -1

    def first_fit(self, size: int) -> int:
        if size <= 0:
            raise ValueError("Allocation size must be greater than zero.")

        for index, block in enumerate(self.memory):
            if block.allocated or block.size < size:
                continue

            replacement = [MemoryBlock(block.start, size, True)]
            if block.size > size:
                replacement.append(MemoryBlock(block.start + size, block.size - size))
            self.memory[index : index + 1] = replacement
            return block.start

        return -1

    def deallocate(self, start_address: int) -> bool:
        for index, block in enumerate(self.memory):
            if block.start == start_address and block.allocated:
                self.memory[index] = MemoryBlock(block.start, block.size)
                self._merge_free_blocks()
                return True
        return False

    def allocated_size(self) -> int:
        return sum(block.size for block in self.memory if block.allocated)

    def snapshot(self) -> list[tuple[int, int, str]]:
        return [
            (block.start, block.size, "Allocated" if block.allocated else "Free")
            for block in self.memory
        ]

    def _merge_free_blocks(self) -> None:
        merged: list[MemoryBlock] = []
        for block in self.memory:
            if merged and not merged[-1].allocated and not block.allocated:
                previous = merged[-1]
                merged[-1] = MemoryBlock(previous.start, previous.size + block.size)
            else:
                merged.append(block)
        self.memory = merged
