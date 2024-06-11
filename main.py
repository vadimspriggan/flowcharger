import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QShortcut, QPushButton, QHBoxLayout
from PyQt5.QtCore import QTimer, Qt, QPoint
from PyQt5.QtGui import QKeySequence, QMouseEvent

try:
    import winreg
except ImportError:
    winreg = None

# Переменные для хранения времени
greentimer = 0
redtimer = 0
shadowtimer = 0

# Списки для хранения значений таймеров
green = []
red = []

# Переменные для статистики
maxshadow = 0
minshadow = 0
countpress = 0
maxred = 0
sumred = 0

# Флаг для переключения режимов
is_green_mode = True

# Проверка текущей темы Windows
def is_dark_theme():
    if winreg is None:
        return False
    try:
        # Открываем ключ реестра для проверки темы
        registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key = winreg.OpenKey(registry, r'SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize')
        value, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
        return value == 0  # 0 - темная тема, 1 - светлая тема
    except Exception as e:
        print(f"Ошибка при определении темы: {e}")
        return False

# Функция для обновления интерфейса
def update_gui():
    global greentimer, redtimer, shadowtimer
    green_label.setText(f"{greentimer//3600:02}:{(greentimer//60)%60:02}:{greentimer%60:02}")
    red_label.setText(f"{redtimer//3600:02}:{(redtimer//60)%60:02}:{redtimer%60:02}")
    stats_label.setText(f"maxshadow: {maxshadow//3600:02}:{(maxshadow//60)%60:02}:{maxshadow%60:02}\n"
                        f"minshadow: {minshadow//3600:02}:{(minshadow//60)%60:02}:{minshadow%60:02}\n"
                        f"countpress: {countpress}\n"
                        f"maxred: {maxred//3600:02}:{(maxred//60)%60:02}:{maxred%60:02}\n"
                        f"sumred: {sumred//3600:02}:{(sumred//60)%60:02}:{sumred%60:02}")

# Функция для переключения режимов
def switch_mode():
    global is_green_mode, greentimer, redtimer, shadowtimer, green, red, maxshadow, minshadow, countpress, maxred, sumred

    if is_green_mode:
        # Переход от зелёного режима к красному
        countpress += 1
        green.append(shadowtimer)
        maxshadow = max(green)
        minshadow = min(green)
        shadowtimer = 0
    else:
        # Переход от красного режима к зелёному
        red.append(redtimer)
        sumred += redtimer
        maxred = max(red)
        redtimer = 0

    is_green_mode = not is_green_mode

# Функция для таймера
def timer_tick():
    global greentimer, redtimer, shadowtimer, is_green_mode
    if is_green_mode:
        greentimer += 1
        shadowtimer += 1
    else:
        redtimer += 1
    update_gui()

# Класс для обработки перемещения окна
class CustomTitleBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.setStyleSheet("background-color: #2b2b2b; color: white;")
        self.dragging = False
        self.startPos = None

        self.setLayout(QHBoxLayout())
        self.title_label = QLabel("FlowCharger", self)
        self.title_label.setStyleSheet("margin-left: 10px;")
        self.layout().addWidget(self.title_label)
        
        self.minimize_button = QPushButton("-", self)
        self.minimize_button.setFixedWidth(20)
        self.minimize_button.clicked.connect(parent.showMinimized)
        self.layout().addWidget(self.minimize_button)

        self.close_button = QPushButton("x", self)
        self.close_button.setFixedWidth(20)
        self.close_button.clicked.connect(parent.close)
        self.layout().addWidget(self.close_button)

        self.layout().addStretch(1)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.startPos = event.globalPos() - self.parent().frameGeometry().topLeft()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            self.parent().move(event.globalPos() - self.startPos)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = False

app = QApplication(sys.argv)

# Определение текущей темы Windows
dark_theme = is_dark_theme()
if dark_theme:
    app.setStyle("Fusion")
    palette = app.palette()
    palette.setColor(app.palette().Window, Qt.black)
    palette.setColor(app.palette().WindowText, Qt.white)
    app.setPalette(palette)

# Создание интерфейса
window = QWidget()
window.setWindowFlags(Qt.FramelessWindowHint)
window.setStyleSheet("background-color: #1e1e1e;" if dark_theme else "background-color: #ffffff;")
window.setWindowTitle("FlowCharger")

layout = QVBoxLayout()
layout.setContentsMargins(0, 0, 0, 0)

# Кастомная шапка окна
title_bar = CustomTitleBar(window)
layout.addWidget(title_bar)

# Элементы интерфейса
green_label = QLabel("00:00:00")
green_label.setStyleSheet("color: green; font-size: 20px;")
layout.addWidget(green_label)

red_label = QLabel("00:00:00")
red_label.setStyleSheet("color: red; font-size: 20px;")
layout.addWidget(red_label)

stats_label = QLabel("")
stats_label.setStyleSheet("font-size: 12px; color: white;" if dark_theme else "font-size: 12px; color: black;")
layout.addWidget(stats_label)

window.setLayout(layout)

# Запуск обновления интерфейса
timer = QTimer()
timer.timeout.connect(timer_tick)
timer.start(1000)

# Обработка горячих клавиш
shortcut = QShortcut(QKeySequence("Ctrl+Space"), window)
shortcut.activated.connect(switch_mode)

# Запуск основного цикла интерфейса
window.show()
sys.exit(app.exec_())
