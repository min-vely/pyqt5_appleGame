# -*- coding: utf-8 -*-
import sys
import random
from PyQt5.QtWidgets import (QApplication, QWidget, QGridLayout, QLabel,
                             QVBoxLayout, QHBoxLayout, QMessageBox, QPushButton)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont

class AppleGame(QWidget):
    GRID_SIZE = 15
    GAME_TIME = 90

    def __init__(self):
        super().__init__()
        self.init_ui()
        self.new_game()

    def init_ui(self):
        """UI를 초기화하고 위젯들을 배치합니다."""
        self.setWindowTitle('사과 게임')
        self.setGeometry(100, 100, 800, 850)

        main_layout = QVBoxLayout()
        top_bar_layout = QHBoxLayout()
        self.grid_layout = QGridLayout()
        bottom_bar_layout = QHBoxLayout()

        self.grid_layout.setSpacing(2)

        font = QFont('Arial', 14)
        self.score_label = QLabel("점수: 0")
        self.score_label.setFont(font)
        self.time_label = QLabel(f"남은 시간: {self.GAME_TIME}")
        self.time_label.setFont(font)
        top_bar_layout.addWidget(self.score_label)
        top_bar_layout.addStretch(1)
        top_bar_layout.addWidget(self.time_label)

        self.status_label = QLabel("숫자를 드래그하여 선택하세요.")
        self.status_label.setFont(QFont('Arial', 12))
        new_game_button = QPushButton("새 게임")
        new_game_button.clicked.connect(self.new_game)
        bottom_bar_layout.addWidget(self.status_label)
        bottom_bar_layout.addStretch(1)
        bottom_bar_layout.addWidget(new_game_button)

        main_layout.addLayout(top_bar_layout)
        main_layout.addLayout(self.grid_layout)
        main_layout.addLayout(bottom_bar_layout)
        self.setLayout(main_layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.is_dragging = False

    def new_game(self):
        """새 게임을 시작합니다."""
        self.score = 0
        self.time_left = self.GAME_TIME
        self.selected_cells = []
        self.is_dragging = False
        self.grid_data = [[random.randint(1, 9) for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]

        self.score_label.setText(f"점수: {self.score}")
        self.time_label.setText(f"남은 시간: {self.time_left}")
        self.status_label.setText("숫자를 드래그하여 선택하세요.")

        self.setup_grid_labels()
        self.timer.start(1000)

    def setup_grid_labels(self):
        """게임 보드의 라벨들을 설정하거나 리셋합니다."""
        for i in range(self.grid_layout.count()):
            self.grid_layout.itemAt(i).widget().deleteLater()

        font = QFont('Arial', 12, QFont.Bold)
        self.grid_labels = []
        for r in range(self.GRID_SIZE):
            row_labels = []
            for c in range(self.GRID_SIZE):
                num = self.grid_data[r][c]
                label = QLabel(str(num))
                label.setFont(font)
                label.setFixedSize(35, 35)
                label.setAlignment(Qt.AlignCenter)
                label.setStyleSheet("background-color: #f0f0f0; color: #333; border: 1px solid #ccc;")
                self.grid_layout.addWidget(label, r, c)
                row_labels.append(label)
            self.grid_labels.append(row_labels)

    def get_cell_at(self, pos):
        """주어진 좌표에 해당하는 셀의 위치(행, 열)를 반환합니다."""
        # 위젯의 로컬 좌표로 변환
        local_pos = self.grid_layout.parentWidget().mapFromGlobal(self.mapToGlobal(pos))
        for r in range(self.GRID_SIZE):
            for c in range(self.GRID_SIZE):
                label = self.grid_labels[r][c]
                if label.geometry().contains(local_pos) and label.isVisible():
                    return r, c
        return None, None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.timer.isActive():
            r, c = self.get_cell_at(event.pos())
            if r is not None:
                self.is_dragging = True
                self.reset_selection_visuals()
                self.selected_cells.clear()
                self.selected_cells.append((r, c))
                self.update_selection_visuals()
                self.update_status()

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            r, c = self.get_cell_at(event.pos())
            if r is not None and (r, c) not in self.selected_cells:
                self.selected_cells.append((r, c))
                self.update_selection_visuals()
                self.update_status()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.is_dragging:
            self.is_dragging = False
            self.check_selection()

    def update_selection_visuals(self):
        """선택된 셀들의 배경색을 변경합니다."""
        for r, c in self.selected_cells:
            self.grid_labels[r][c].setStyleSheet("background-color: #aade87; color: #000; border: 1px solid #888;")

    def reset_selection_visuals(self):
        """선택된 셀들의 배경색을 원래대로 되돌립니다."""
        for r, c in self.selected_cells:
            if self.grid_labels[r][c].isVisible():
                self.grid_labels[r][c].setStyleSheet("background-color: #f0f0f0; color: #333; border: 1px solid #ccc;")

    def update_status(self):
        """현재 선택된 숫자들과 합계를 상태 라벨에 표시합니다."""
        if not self.selected_cells:
            self.status_label.setText("숫자를 드래그하여 선택하세요.")
            return

        current_sum = sum(self.grid_data[r][c] for r, c in self.selected_cells)
        selected_numbers = [str(self.grid_data[r][c]) for r, c in self.selected_cells]
        self.status_label.setText(f"선택: {' + '.join(selected_numbers)} = {current_sum}")

    def check_selection(self):
        """선택된 숫자들의 합과 연결 상태를 확인하고 처리합니다."""
        if not self.selected_cells:
            return

        current_sum = sum(self.grid_data[r][c] for r, c in self.selected_cells)

        if current_sum == 10 and len(self.selected_cells) >= 2 and self.is_selection_connected():
            self.score += len(self.selected_cells)
            self.score_label.setText(f"점수: {self.score}")
            for r, c in self.selected_cells:
                self.grid_data[r][c] = 0
                self.grid_labels[r][c].setVisible(False)
        else:
            self.reset_selection_visuals()

        self.selected_cells.clear()
        self.update_status()

    def is_selection_connected(self):
        """선택된 셀들이 규칙에 맞게 연결되었는지 확인합니다."""
        if len(self.selected_cells) < 2:
            return False

        rows = {r for r, c in self.selected_cells}
        cols = {c for r, c in self.selected_cells}

        is_same_row = len(rows) == 1
        is_same_col = len(cols) == 1

        if not (is_same_row or is_same_col):
            return False

        if is_same_row:
            r = rows.pop()
            min_c, max_c = min(cols), max(cols)
            for c in range(min_c, max_c + 1):
                if self.grid_data[r][c] == 0 and (r, c) not in self.selected_cells:
                    continue # 빈 칸은 건너뛰기
                if (r, c) not in self.selected_cells:
                    return False # 경로상에 선택되지 않은 다른 숫자가 있음
            return True

        if is_same_col:
            c = cols.pop()
            min_r, max_r = min(rows), max(rows)
            for r in range(min_r, max_r + 1):
                if self.grid_data[r][c] == 0 and (r, c) not in self.selected_cells:
                    continue # 빈 칸은 건너뛰기
                if (r, c) not in self.selected_cells:
                    return False # 경로상에 선택되지 않은 다른 숫자가 있음
            return True

        return False

    def update_timer(self):
        """타이머를 1초씩 업데이트하고, 0이 되면 게임을 종료합니다."""
        self.time_left -= 1
        self.time_label.setText(f"남은 시간: {self.time_left}")
        if self.time_left <= 0:
            self.timer.stop()
            self.game_over()

    def game_over(self):
        """게임 종료 메시지를 표시합니다."""
        self.is_dragging = False
        msg_box = QMessageBox()
        msg_box.setWindowTitle("게임 종료")
        msg_box.setText(f"시간 종료!\n\n최종 점수: {self.score}점")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = AppleGame()
    game.show()
    sys.exit(app.exec_())