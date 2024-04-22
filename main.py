import sys
import time
import json
import requests
import threading
from main1 import app2
import uvicorn
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QStackedWidget,
    QPushButton,
    QLineEdit,
    QComboBox,
    QCheckBox,
    QTextEdit,
    QToolBar,
    QSpacerItem,
    QSizePolicy,
    QListWidgetItem
)

from PySide6.QtGui import QIcon, QFont, QPixmap
from PySide6.QtCore import Qt, QUrl, QTimer, QRect
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from qt_material import apply_stylesheet


clips_id = []
a = None
b = None
title1 = None
title2 = None

def run_api():
    uvicorn.run(app2, host="0.0.0.0", port=8000)
    print("api已启动")
thread2 = threading.Thread(target=run_api)
thread2.start()


def test_generate_music(lyric, style, instrument, title):
    global clips_id
    data = {
        "tags": style,
        "prompt": lyric,
        "make_instrumental": instrument,
        "mv": "chirp-v3-0",
        "title": title

    }
    r = requests.post(
        "http://127.0.0.1:8000/generate/", data=json.dumps(data)
    )
    resp = r.text
    json_data = resp
    data = json.loads(json_data)
    clips_id = [clip['id'] for clip in data['clips']]


def get_info(aid):
    response = requests.get(f"http://127.0.0.1:8000/feed/{aid}")

    data = json.loads(response.text)[0]
    print(data["audio_url"])
    return data["audio_url"]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.setWindowTitle("SUNO整合工具")
        self.setGeometry(100, 100, 960, 540)

        self.toolbar = QToolBar("My Toolbar")
        self.addToolBar(Qt.TopToolBarArea, self.toolbar)
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)

        imageLabel = QLabel()
        imageLabel.setPixmap(QPixmap("pic.png"))

        self.toolbar.addWidget(imageLabel)

        text = QLabel('Tamiki的Suno工具')
        self.toolbar.addWidget(text)

        self.toolbar.addSeparator()
        spacer = QLabel()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.toolbar.addWidget(spacer)

        def toggle_night_mode(checked):
            if checked:
                apply_stylesheet(app, theme='dark_lightgreen.xml', invert_secondary=True)
            else:
                apply_stylesheet(app, theme='light_blue.xml', invert_secondary=True)

        switch = QCheckBox("夜间模式     ")
        self.toolbar.addWidget(switch)
        switch.stateChanged.connect(toggle_night_mode)

        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        mainLayout = QHBoxLayout()
        self.lyric_display = QTextEdit()
        font = self.lyric_display.font()
        font.setPointSize(50)
        self.lyric_display.setFont(font)

        self.pagesWidget = QStackedWidget()
        self.addPages()

        self.navListWidget = QListWidget()
        self.navListWidget.addItem("歌曲生成")
        self.navListWidget.addItem("歌词生成")
        self.navListWidget.addItem("曲风选择器")
        self.navListWidget.addItem("设置")
        self.navListWidget.addItem("关于")
        self.navListWidget.currentRowChanged.connect(self.displayPage)

        mainLayout.addWidget(self.navListWidget, 0)
        mainLayout.addWidget(self.pagesWidget, 1)
        centralWidget.setLayout(mainLayout)

    def initUI(self):

        self.main_layout = QVBoxLayout(self)

        self.setLayout(self.main_layout)
        return self.main_layout

    def addMusicBar(self, pic, title, audio_url):
        print(555)

        player = QMediaPlayer()
        audio_output = QAudioOutput()
        player.setAudioOutput(audio_output)

        bar_layout = QHBoxLayout()

        image_label = QLabel(self)
        image_pixmap = QPixmap(pic)
        image_label.setPixmap(image_pixmap.scaled(50, 50, aspectMode=Qt.IgnoreAspectRatio))

        song_info_label = QLabel(title, self)
        song_info_label.setFrameStyle(QLabel.Panel | QLabel.Sunken)
        song_info_label.setFixedSize(200, 20)

        play_button = QPushButton('播放', self)
        play_button.clicked.connect(lambda: self.toggleMusic(player, audio_output, play_button, audio_url))

        bar_layout.addWidget(image_label)
        bar_layout.addWidget(song_info_label)
        bar_layout.addStretch()
        bar_layout.addWidget(play_button)

        self.main_layout.addLayout(bar_layout)

        self.main_layout.update()

    def toggleMusic(self, player, audio_output, button, audio_url):

        if player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            player.pause()
            button.setText('播放')
        else:
            url = QUrl(audio_url)
            player.setSource(url)
            player.play()
            audio_output.setVolume(0.5)
            button.setText('暂停')

    def addPages(self):
        self.pagesWidget.addWidget(self.create_music_page())
        self.pagesWidget.addWidget(self.create_lyric_page())
        self.pagesWidget.addWidget(self.create_style_page())
        self.pagesWidget.addWidget(self.create_option_page())
        self.pagesWidget.addWidget(QLabel("Made by TamikiP."))

    def displayPage(self, index):
        self.pagesWidget.setCurrentIndex(index)

    def create_lyric_page(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)

        left_layout = QVBoxLayout()
        combo_box = QComboBox()
        combo_box.addItems(['中文', '英文', '日文'])
        style_box = QComboBox()
        style_box.addItems(['抒情', '热血', '叙事', '抑郁', '嘻哈'])
        model_box = QComboBox()
        model_box.addItems(['gpt-3.5-turbo', 'GPT4-Turbo', 'claude-3-sonnet'])
        text_box = QLineEdit()
        text_box.setPlaceholderText('更进一步地描述歌词...')
        text_box.setFixedSize(270, 40)
        button = QPushButton('生成')

        spacer_size = 15
        left_layout.addSpacing(spacer_size)
        left_layout.addWidget(combo_box)
        left_layout.addSpacing(spacer_size)
        left_layout.addWidget(style_box)
        left_layout.addSpacing(spacer_size)
        left_layout.addWidget(model_box)
        left_layout.addSpacing(spacer_size)
        left_layout.addWidget(text_box)
        left_layout.addSpacing(spacer_size)
        left_layout.addWidget(button)

        lyric_display = QTextEdit()

        layout.addLayout(left_layout)
        layout.addWidget(lyric_display, 1)

        button.clicked.connect(lambda: self.on_button_clicked(combo_box, style_box, text_box, model_box, lyric_display))
        return widget

    def create_style_page(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)

        left_layout = QVBoxLayout()
        style1 = QLabel('曲风')
        combo_box = QComboBox()
        combo_box.addItems(['爵士', '流行', '电子', "放克", "古典", "R&B", "JPOP", "KPOP", "VOCALOID", "Anime"])
        combo_box.setFixedSize(270, 40)
        style2 = QLabel('乐器')
        style_box = QComboBox()
        style_box.addItems(['钢琴', '架子鼓', '吉他', '贝斯', '小提琴', "电吉他"])
        style3 = QLabel('人声')
        vocal_box = QComboBox()
        vocal_box.addItems(['男声', '女声（普通）', '女高音', 'Miku', '童声'])

        spacer_size = 10
        left_layout.addWidget(style1)
        left_layout.addWidget(combo_box)
        left_layout.addSpacing(spacer_size)
        left_layout.addWidget(style2)
        left_layout.addWidget(style_box)
        left_layout.addSpacing(spacer_size)
        left_layout.addWidget(style3)
        left_layout.addWidget(vocal_box)

        layout.addLayout(left_layout)
        layout.addWidget(self.lyric_display, 1)
        combo_box.currentIndexChanged.connect(lambda: self.lyric_display.append(combo_box.currentText()))
        style_box.currentIndexChanged.connect(lambda: self.lyric_display.append(style_box.currentText()))
        vocal_box.currentIndexChanged.connect(lambda: self.lyric_display.append(vocal_box.currentText()))

        return widget

    def create_option_page(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)

        left_layout = QVBoxLayout()
        suno = QLabel('Suno(填写了才能使用音乐生成功能)')
        text_box = QLineEdit()
        text_box.setPlaceholderText('session:')
        text_box2 = QLineEdit()
        text_box2.setPlaceholderText('cookie:')
        GPT = QLabel('ChatGPT(填写了才能使用ai写词功能)')
        text_box3 = QLineEdit()
        text_box3.setPlaceholderText('base_url:')
        text_box4 = QLineEdit()
        text_box4.setPlaceholderText('key:')

        spacer_size = 45
        left_layout.addWidget(suno)
        left_layout.addWidget(text_box)
        left_layout.addSpacing(spacer_size)
        left_layout.addWidget(text_box2)
        left_layout.addSpacing(spacer_size)
        left_layout.addWidget(GPT)
        left_layout.addWidget(text_box3)
        left_layout.addSpacing(spacer_size)
        left_layout.addWidget(text_box4)
        left_layout.addSpacing(spacer_size)
        text_box.textChanged.connect(self.session_change)
        text_box.textChanged.connect(self.cookies_change)
        text_box3.textChanged.connect(self.url_change)
        text_box4.textChanged.connect(self.key_change)

        layout.addLayout(left_layout)

        return widget

    def create_music_page(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)

        left_layout = QVBoxLayout()

        textbox = QTextEdit()
        textbox.setPlaceholderText("歌词:")
        textbox.setFixedSize(270, 200)
        textbox2 = QTextEdit()
        textbox2.setPlaceholderText("歌曲风格")
        textbox2.setFixedSize(270, 70)
        button = QPushButton('生成')
        switch_button = QCheckBox('伴奏模式')
        text_box3 = QLineEdit()
        text_box3.setPlaceholderText('标题')

        spacer_size = 10
        left_layout.addWidget(textbox)
        left_layout.addSpacing(spacer_size)
        left_layout.addWidget(textbox2)
        left_layout.addWidget(switch_button)
        left_layout.addSpacing(spacer_size)
        left_layout.addWidget(text_box3)
        left_layout.addSpacing(spacer_size)
        left_layout.addWidget(button)

        music_player = self.initUI()

        layout.addLayout(left_layout)
        layout.addLayout(music_player, 1)

        button.clicked.connect(lambda: self.start_thread(textbox, textbox2, switch_button, text_box3))

        return widget

    def create_about_page(self):
        widget = QWidget()
        layout = QHBoxLayout(widget)

        left_layout = QVBoxLayout()
        suno = QLabel()

        spacer_size = 45
        left_layout.addWidget(suno)

        layout.addLayout(left_layout)

        return widget

    def gpt(self, langeuage, style, describe, gpt_kind):
        file_path = 'config.py'
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        if len(lines) >= 2:
            url = lines[0].strip()
            key = lines[1].strip()
        if gpt_kind == "GPT4-Turbo":
            gpt_kind = "gpt-4-turbo-2024-04-09"
        payload = json.dumps({
            "model": gpt_kind,
            "messages": [
                {
                    "role": "system",
                    "content": "你现在是一个作词家，能写出优秀的歌词。你直接输出歌词即可，要完整的。标出歌词部分（主副歌，用中文标）。"
                },
                {
                    "role": "user",
                    "content": f"歌词的语言是{langeuage},歌词的风格是{style},歌词的更近一步描述{describe}"
                }
            ]
        })
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {key}',
            'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
            'Content-Type': 'application/json'
        }
        url = f"https://{url}/v1/chat/completions"
        response = requests.request("POST", url, headers=headers, data=payload)
        data = json.loads(response.text)
        content = data["choices"][0]["message"]["content"]
        return content

    def on_button_clicked(self, combo_box, style_box, text_box, model_box, lyric_display):
        language = combo_box.currentText()
        style = style_box.currentText()
        describe = text_box.text()
        gpt_kind = model_box.currentText()
        lyric = self.gpt(language, style, describe, gpt_kind)
        lyric_display.setText(lyric)

    def start_thread(self, textbox, textbox2, switch, textbox3):
        global a, b, title1, title2
        thread = threading.Thread(target=self.on_button_clicked2, args=(textbox, textbox2, switch, textbox3))
        thread.start()
        time.sleep(15)
        self.addMusicBar("1.png", title1, a)
        self.addMusicBar("1.png", title2, b)
        print(a, b, "test111")

    def on_button_clicked2(self, textbox, textbox2, switch, textbox3):
        global clips_id, a, b, title1, title2
        lyric = textbox.toPlainText()
        style = textbox2.toPlainText()
        instrument = switch.isChecked()
        title = textbox3.text()
        print(lyric, style, instrument, title)
        test_generate_music(lyric, style, instrument, title)
        time.sleep(8)
        a = get_info(clips_id[0])
        b = get_info(clips_id[1])
        title1 = f"{title}NO.1"
        title2 = f"{title}NO.2"
        time.sleep(120)
        self.save_song(a)
        self.save_song(b)

    def key_change(self, text):
        file_path = 'config.py'
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        new_first_line = f"{text}\n"
        lines[1] = new_first_line
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(lines)

    def url_change(self, text):
        file_path = 'config.py'
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        new_first_line = f"{text}\n"
        lines[1] = new_first_line
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(lines)

    def session_change(self, text):
        file_path = '.env'
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        new_session_id = text
        for i, line in enumerate(lines):
            if i == 1:
                key, value = line.strip().split('=')
                if key == 'SESSION_ID':
                    lines[i] = f"SESSION_ID={new_session_id}\n"
                    break
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(lines)

    def cookies_change(self, text):
        file_path = '.env'
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        new_cookies_id = text
        for i, line in enumerate(lines):
            if i == 1:
                key, value = line.strip().split('=')
                if key == 'COOKIE':
                    lines[i] = f"COOKIE={new_cookies_id}\n"
                    break
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(lines)

    def save_song(self, url, output_path="output"):
        response = requests.get(url)

        if response.status_code == 200:

            filename = 'downloaded_song.mp3'

            with open(filename, 'wb') as file:
                file.write(response.content)
            print(f'文件已下载，保存为 {filename}')
        else:
            print('下载失败，状态码：', response.status_code)


app = QApplication(sys.argv)
apply_stylesheet(app, theme='light_blue.xml', invert_secondary=True)
window = MainWindow()
icon_path = "icon.png"
window.setWindowIcon(QIcon(icon_path))
window.setFixedSize(960, 540)
window.show()
sys.exit(app.exec())
