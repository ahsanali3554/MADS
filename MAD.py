from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, \
    QListWidget, QMessageBox, QProgressBar, QInputDialog
import sys


class MemoryManager:
    def __init__(self, total_size):
        self.total_size = total_size
        self.memory = [(0, total_size, False)]  # (start, size, allocated)

    def allocate(self, size, position=None):
        if position is not None:
            for i, (start, block_size, allocated) in enumerate(self.memory):
                if not allocated and start <= position < start + block_size and block_size >= size:
                    offset = position - start  # Find the offset inside the free block
                    if offset > 0:
                        self.memory.insert(i, (start, offset, False))  # Free space before position
                    self.memory[i] = (position, size, True)  # Allocate at position
                    if block_size > size + offset:
                        self.memory.insert(i + 1,
                                           (position + size, block_size - size - offset, False))  # Free space after
                    return position
            return -1
        else:
            return self.first_fit(size)

    def first_fit(self, size):
        for i, (start, block_size, allocated) in enumerate(self.memory):
            if not allocated and block_size >= size:
                self.memory[i] = (start, size, True)
                if block_size > size:
                    self.memory.insert(i + 1, (start + size, block_size - size, False))
                return start
        return -1

    def deallocate(self, start_address):
        for i, (start, size, allocated) in enumerate(self.memory):
            if start == start_address and allocated:
                self.memory[i] = (start, size, False)
                self.merge_free_blocks()
                return True
        return False

    def merge_free_blocks(self):
        i = 0
        while i < len(self.memory) - 1:
            if not self.memory[i][2] and not self.memory[i + 1][2]:
                start, size, _ = self.memory[i]
                next_start, next_size, _ = self.memory[i + 1]
                self.memory[i] = (start, size + next_size, False)
                del self.memory[i + 1]
            else:
                i += 1

    def display(self):
        return [(start, size, "Allocated" if allocated else "Free") for start, size, allocated in self.memory]


class MemoryGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Memory Management Simulator")
        self.setGeometry(100, 100, 500, 500)
        self.memory_manager = None

        layout = QVBoxLayout()

        self.init_memory_btn = QPushButton("Initialize Memory", self)
        self.init_memory_btn.clicked.connect(self.init_memory)
        layout.addWidget(self.init_memory_btn)

        self.memory_display = QListWidget(self)
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.memory_display)
        layout.addWidget(self.progress_bar)

        # Allocate and Deallocate buttons
        self.allocate_btn = QPushButton("Allocate Memory", self)
        self.allocate_btn.clicked.connect(self.allocate_memory)
        self.allocate_btn.setEnabled(False)  # Disabled until memory is initialized
        layout.addWidget(self.allocate_btn)

        self.deallocate_btn = QPushButton("Deallocate Memory", self)
        self.deallocate_btn.clicked.connect(self.deallocate_memory)
        self.deallocate_btn.setEnabled(False)  # Disabled until memory is initialized
        layout.addWidget(self.deallocate_btn)

        self.setLayout(layout)

    def init_memory(self):
        size, ok = QInputDialog.getInt(self, "Initialize Memory", "Enter total memory size:")
        if ok and size > 0:
            self.memory_manager = MemoryManager(size)
            self.update_memory_display()
            self.allocate_btn.setEnabled(True)  # Enable allocation button
            self.deallocate_btn.setEnabled(True)  # Enable deallocation button

    def allocate_memory(self):
        if not self.memory_manager:
            return
        size, ok = QInputDialog.getInt(self, "Allocate Memory", "Enter process size to allocate:")
        if not ok:
            return
        position, pos_ok = QInputDialog.getInt(self, "Allocate Position", "Enter position to allocate or -1 for auto:", -1)
        if pos_ok:
            position = None if position == -1 else position
        address = self.memory_manager.allocate(size, position)
        if address == -1:
            QMessageBox.warning(self, "Warning", "Memory allocation failed! Consider freeing up space.")
        self.update_memory_display()

    def deallocate_memory(self):
        if not self.memory_manager:
            return
        start_address, ok = QInputDialog.getInt(self, "Deallocate Memory", "Enter start address to free:")
        if ok:
            success = self.memory_manager.deallocate(start_address)
            if not success:
                QMessageBox.warning(self, "Warning", "Deallocation failed! Invalid address.")
        self.update_memory_display()

    def update_memory_display(self):
        self.memory_display.clear()
        total_memory = self.memory_manager.total_size
        allocated_memory = sum(size for _, size, allocated in self.memory_manager.memory if allocated)
        self.progress_bar.setValue(int((allocated_memory / total_memory) * 100))
        for block in self.memory_manager.display():
            self.memory_display.addItem(f"Start: {block[0]}, Size: {block[1]}, {block[2]}")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MemoryGUI()
    window.show()
    sys.exit(app.exec_())
