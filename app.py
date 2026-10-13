"""PyQt5 interface for the memory allocation and deallocation simulator."""

import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from memory_manager import MemoryManager


class MemorySimulatorWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.manager: MemoryManager | None = None
        self.setWindowTitle("Memory Allocation Simulator")
        self.setMinimumSize(680, 520)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)

        title = QLabel("Memory Allocation Simulator")
        title.setObjectName("title")
        subtitle = QLabel("Explore first-fit allocation, fixed-position allocation and block merging.")
        subtitle.setWordWrap(True)
        subtitle.setObjectName("subtitle")

        self.status = QLabel("Initialize memory to begin.")
        self.status.setObjectName("status")
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setFormat("%p% allocated")

        self.blocks = QListWidget()
        self.blocks.setAlternatingRowColors(True)

        initialize = QPushButton("Initialize memory")
        initialize.clicked.connect(self.initialize_memory)

        self.allocate_button = QPushButton("Allocate block")
        self.allocate_button.clicked.connect(self.allocate_memory)
        self.allocate_button.setEnabled(False)

        self.deallocate_button = QPushButton("Deallocate block")
        self.deallocate_button.clicked.connect(self.deallocate_memory)
        self.deallocate_button.setEnabled(False)

        actions = QHBoxLayout()
        actions.addWidget(initialize)
        actions.addWidget(self.allocate_button)
        actions.addWidget(self.deallocate_button)

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(actions)
        layout.addWidget(self.status)
        layout.addWidget(self.progress)
        layout.addWidget(self.blocks, 1)

        self.setCentralWidget(container)
        self.setStyleSheet(
            """
            QMainWindow { background: #f4f7fb; }
            QWidget { color: #172033; font-family: "Segoe UI"; font-size: 14px; }
            QLabel#title { font-size: 28px; font-weight: 700; color: #102044; }
            QLabel#subtitle { color: #5c6880; font-size: 15px; }
            QLabel#status { color: #35415a; font-weight: 600; padding-top: 6px; }
            QPushButton {
                background: #2357d8; color: white; border: none; border-radius: 7px;
                padding: 10px 16px; font-weight: 600;
            }
            QPushButton:hover { background: #1947ba; }
            QPushButton:disabled { background: #aeb8cc; }
            QProgressBar {
                background: white; border: 1px solid #d7deea; border-radius: 7px;
                min-height: 24px; text-align: center;
            }
            QProgressBar::chunk { background: #30a46c; border-radius: 6px; }
            QListWidget {
                background: white; border: 1px solid #d7deea; border-radius: 9px;
                padding: 8px; outline: none;
            }
            QListWidget::item { padding: 10px; border-radius: 5px; }
            QListWidget::item:selected { background: #dfe9ff; color: #102044; }
            """
        )

    def initialize_memory(self) -> None:
        size, accepted = QInputDialog.getInt(
            self, "Initialize memory", "Total memory size:", 1024, 1, 1_000_000
        )
        if not accepted:
            return
        self.manager = MemoryManager(size)
        self.allocate_button.setEnabled(True)
        self.deallocate_button.setEnabled(True)
        self.refresh()

    def allocate_memory(self) -> None:
        if self.manager is None:
            return

        size, accepted = QInputDialog.getInt(
            self, "Allocate block", "Block size:", 128, 1, self.manager.total_size
        )
        if not accepted:
            return

        position, positioned = QInputDialog.getInt(
            self,
            "Allocation position",
            "Start address (-1 uses first fit):",
            -1,
            -1,
            self.manager.total_size - 1,
        )
        if not positioned:
            return

        address = self.manager.allocate(size, None if position == -1 else position)
        if address == -1:
            QMessageBox.warning(
                self,
                "Allocation failed",
                "No free block can satisfy this allocation.",
            )
        self.refresh()

    def deallocate_memory(self) -> None:
        if self.manager is None:
            return

        address, accepted = QInputDialog.getInt(
            self,
            "Deallocate block",
            "Allocated block start address:",
            0,
            0,
            self.manager.total_size - 1,
        )
        if not accepted:
            return

        if not self.manager.deallocate(address):
            QMessageBox.warning(
                self,
                "Deallocation failed",
                "No allocated block starts at that address.",
            )
        self.refresh()

    def refresh(self) -> None:
        if self.manager is None:
            return

        used = self.manager.allocated_size()
        self.status.setText(
            f"{used:,} of {self.manager.total_size:,} units allocated · "
            f"{len(self.manager.memory)} blocks"
        )
        self.progress.setValue(round(used / self.manager.total_size * 100))
        self.blocks.clear()

        for start, size, state in self.manager.snapshot():
            item = f"0x{start:04X} – 0x{start + size - 1:04X}    {size:,} units    {state}"
            self.blocks.addItem(item)


def main() -> int:
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    window = MemorySimulatorWindow()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
