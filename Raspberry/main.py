#索引值0:封面 1主畫面 2解題 3讀書會 4英文
import sys
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QStackedWidget, QWidget,QLineEdit,QVBoxLayout,QHBoxLayout
from PyQt5.QtGui import QPixmap,QPalette, QColor, QIcon
from PyQt5.QtCore import Qt, QRect,QSize
from openai import OpenAI
from gtts import gTTS
import os
import playsound
import pygame
import io
import pymysql

# 資料庫連接配置
DB_CONFIG = {
    'host': '18.180.122.148',
    'user': 'admin',
    'password': 'LCivpNcrALc6YDK',
    'database': 'my_database',
    'charset': 'utf8mb4',
}

# 資料庫連接函數
def connect_db():
    try:
        connection = pymysql.connect(**DB_CONFIG)
        return connection
    except pymysql.MySQLError as e:
        print(f"資料庫連接失敗: {e}")
        return None
client = OpenAI(
    # defaults to os.environ.get("OPENAI_API_KEY")
    api_key="sk-uJ3B62eXV4XouZSH7htWKYzf5QFj1W0WQd4AAn072WQPzptn",
    base_url="https://api.chatanywhere.tech/v1"
)

# 用戶註冊函數
def register_and_login(name: str, account: str, password: str) -> bool:
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            # 檢查賬號是否已存在
            sql = 'SELECT uID FROM User WHERE account = %s'
            cursor.execute(sql, (account,))
            result = cursor.fetchone()
            if result:
                print("註冊失敗，帳號已存在。")
                return False

            # 插入新用戶數據
            sql = "INSERT INTO User (name, account, password) VALUES (%s, %s, %s)"
            cursor.execute(sql, (name, account, password))  # 直接插入明文密碼
            connection.commit()
            print("註冊成功！")
            return True
    except Exception as e:
        print(f"註冊失敗: {e}")
        connection.rollback()
        return False
    finally:
        connection.close()

# 用戶登入檢查函數
def login_check(account: str, password: str) -> bool:
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            sql = 'SELECT password FROM User WHERE account = %s'
            cursor.execute(sql, (account,))
            result = cursor.fetchone()
            if result and result[0] == password:  # 比對明文密碼
                print("登入成功！")
                return True
            else:
                print("登入失敗，帳號或密碼錯誤。")
                return False
    finally:
        connection.close()
        
        

class ProblemSolvingPage(QWidget):
    def __init__(self, main_window,parent=None):
        super().__init__(parent)
        self.setWindowTitle('國文解題')
        self.setGeometry(100, 100, 1024, 768)
        # 設定背景顏色
        self.setStyleSheet("background-color: #E0F7FA;")  # 淺藍色背景
        self.main_window = main_window 
        # 設定佈局
        layout = QVBoxLayout()
        width=self.width()
        height=self.height()
        # 返回按鈕
        self.back_button = QPushButton('', self)
        self.back_button.setGeometry(10, 10,int(width*0.0625), int(height*0.0807265))
        self.back_button.setIcon(QIcon('image/1.'))  # 使用你的返回箭頭圖標
        self.back_button.setIconSize(QSize(40, 40))
        #self.back_button.setStyleSheet('background-color: transparent; border: none;')
        self.back_button.clicked.connect(self.go_back)  # 連接到返回功能
        layout.addWidget(self.back_button, alignment=Qt.AlignLeft)  # 將按鈕放在左上角

        # 國文按鈕 (模仿圖片中的按鈕)
        self.chinese_button = QPushButton('國文', self)
        self.chinese_button.setGeometry(70, 10, 80, 40)
        self.chinese_button.setStyleSheet('background-color: #64B5F6; border-radius: 20px; color: white; font-size: 40px;')

        # 創建顯示解答區域
        self.answer_label = QLabel("解答會顯示在這裡", self)
        self.answer_label.setStyleSheet('font-size: 18px; color: black;')
        self.answer_label.setGeometry(1000, 100, 900, 300)  # 手動設置顯示解答區域的位置和大小
        self.answer_label.setStyleSheet('font-size: 18px; color: black; background-color: white; padding: 10px;')
        self.answer_label.setWordWrap(True)
        layout.addWidget(self.answer_label)

        # 創建輸入框 (放置在底部)
        self.input_field = QLineEdit(self)
        self.input_field.setPlaceholderText("請輸入國文問題")
        self.input_field.setGeometry(60, 920, 800, 50)  # 調整輸入框的位置和大小
        self.input_field.setStyleSheet('font-size: 18px; padding: 10px; border-radius: 25px; background-color: #B3E5FC;')

        # 相機按鈕 (左下角)
        self.camera_button = QPushButton('', self)
        self.camera_button.setGeometry(10, 920, 50, 50)
        self.camera_button.setIcon(QIcon('image/1.jpg'))  # 使用相機圖示
        self.camera_button.setIconSize(QSize(40, 40))
        #self.camera_button.setStyleSheet('background-color: transparent; border: none;')

        # 送出按鈕 (右下角紙飛機)
        self.send_button = QPushButton('', self)
        self.send_button.setGeometry(880,920, 50, 50)
        self.send_button.setIcon(QIcon('image/1.jpg'))  # 使用紙飛機圖示
        self.send_button.setIconSize(QSize(40, 40))
        self.send_button.setStyleSheet('background-color: transparent; border: none;')
        #self.send_button.clicked.connect(self.solve_problem)

        self.setLayout(layout)

    def resizeEvent(self, event):
         # 在窗口調整大小時，重新調整背景圖片大小
        self.back_button.setGeometry(10, 10, 50, 50)
        self.send_button.setGeometry(880,920, 50, 50)
        self.camera_button.setGeometry(10, 920, 50, 50)
        self.input_field.setGeometry(60, 920, 800, 50)  # 調整輸入框的位置和大小
        self.answer_label.setGeometry(60, 50, 900, 300)  # 手動設置顯示解答區域的位置和大小
        self.chinese_button.setGeometry(70, 10, 80, 40)


    def gpt_35_api_stream(self, messages: list): #GPT 輸出
        try:
            stream = client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=messages,
                stream=True,
            )
            full_response = ""
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response  += chunk.choices[0].delta.content
            self.answer_label.setText(full_response )
        except Exception as e:
            self.answer_label.setText(f"發生錯誤: {e}")

    def solve_problem(self):
        # 取得輸入的問題
        question = self.input_field.text()
        if question:
            # 清空標籤並顯示等待訊息
            self.answer_label.setText(f"正在為「{question}」生成解答...")
            # 構造發送給 GPT 的訊息
            messages = [{'role': 'user', 'content': f'你是個國文老師，麻煩用繁體中文幫她解決問題，問題是「{question}」'}]
            # 調用 GPT API 生成解答
            self.gpt_35_api_stream(messages)
        else:
            self.answer_label.setText("請輸入一個問題。")

    def go_back(self): #回到選擇科目的地方
        self.main_window.stacked_widget.setCurrentIndex(2)

# 自訂第三頁的視窗
class CustomPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Solving Interface')
        self.setGeometry(100, 100, 1024, 768)

        width = self.width()
        height = self.height()
        # 創建背景標籤
        self.background_label = QLabel(self)
        self.background_label.setGeometry(0, 0, self.width(), self.height())

        # 呼叫設定背景圖片函數
        self.set_background_image('image/3.jpg')

        # 創建按鈕
        self.create_buttons()

        # 創建返回按鈕
        self.back_button = QPushButton('', self)
        self.back_button.setGeometry(0, 0,int(width*0.0625), int(height*0.0807265))
        #self.back_button.setStyleSheet('background-color: transparent; font-size: 18px;')

    def set_background_image(self, image_path):
        # 載入圖片
        background_image = QPixmap(image_path)
        if background_image.isNull():
            print(f"圖片未加載成功，請確認路徑：{image_path}")
        else:
            # 將背景圖片設定給 QLabel
            self.background_label.setPixmap(background_image)
            self.background_label.setScaledContents(True)

    def resizeEvent(self, event):
        # 重新設定背景圖片大小
        self.background_label.setGeometry(0, 0, self.width(), self.height())

        width = self.width()
        height = self.height()
        button_width = int(width * 0.15)
        button_height = int(height * 0.25)

        self.button1.setGeometry(int(width * 0.425), int(height * 0.26), button_width, button_height)  # 國文
        self.button2.setGeometry(int(width * 0.675), int(height * 0.26), button_width, button_height)  # 英文
        self.button3.setGeometry(int(width * 0.18), int(height * 0.61), button_width, button_height)  # 數學
        self.button4.setGeometry(int(width * 0.425), int(height * 0.61), button_width, button_height)  # 自然
        self.button5.setGeometry(int(width * 0.675), int(height * 0.61), button_width, button_height)  # 社會

        #self.button1.setStyleSheet('background-color: transparent;')
        #self.button2.setStyleSheet('background-color: transparent;')
        #self.button3.setStyleSheet('background-color: transparent;')
        #self.button4.setStyleSheet('background-color: transparent;')
        #self.button5.setStyleSheet('background-color: transparent;')

    def create_buttons(self):
        self.button1 = QPushButton(' ', self)
        self.button2 = QPushButton(' ', self)
        self.button3 = QPushButton(' ', self)
        self.button4 = QPushButton(' ', self)
        self.button5 = QPushButton(' ', self)



class EnglishPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 設定佈局
        self.setWindowTitle('English Practice')
        self.setGeometry(100, 100, 1024, 768)
        width = self.width()
        height = self.height()
         # 加載背景圖片
        self.background_label = QLabel(self)
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.set_background_image('image/5.jpg')  # Adjust the path based on where the file is saved
        #創建輸入框
        self.input_field = QLineEdit(self)
        self.input_field.setGeometry(int(width*0.078125), int(height*0.282542), int(width*0.3125), int(height*0.2018163))
        self.input_field.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0);  /* 設置完全透明 */
            border: none;  /* 移除邊框 */
            color: black;  /* 設置文字顏色 */
            font-size: 24px;
            padding: 10px;
        """)

        self.input_field.setPlaceholderText("輸入英文")

        # 創建透明撥放按鈕
        self.play_button = QPushButton('', self)
        self.play_button.setGeometry(int(width*0.423), int(height*0.676084), int(width*0.041666), int(height*0.0807265))  # Adjust the size and position
        #self.play_button.setStyleSheet('background-color: transparent; border: none;')
        self.play_button.clicked.connect(self.play_audio)

        # 創建返回按鈕
        self.back_button = QPushButton('', self)
        self.back_button.setGeometry(0, 0, int(width*0.0625), int(height*0.0807265))
        #self.back_button.setStyleSheet('background-color: transparent; font-size: 18px;')


    def set_background_image(self, image_path):
        # 加載圖片並設置為背景
        background_image = QPixmap(image_path)
        if background_image.isNull():
            print(f"圖片加載失敗：{image_path}")
        else:
            self.background_label.setPixmap(background_image)
            self.background_label.setScaledContents(True)

    def resizeEvent(self, event):
         # 在窗口調整大小時，重新調整背景圖片大小
        width = self.width()
        height = self.height()
        self.background_label.setGeometry(0, 0, width, height)
        self.input_field.setGeometry(int(width*0.078125), int(height*0.282542), int(width*0.3125), int(height*0.2018163))
        self.play_button.setGeometry(int(width*0.423), int(height*0.676084), int(width*0.041666), int(height*0.0807265))
        self.back_button.setGeometry(0,0,int(width*0.0625), int(height*0.0807265))

    def play_audio(self):
         # 撥放音頻的功能（目前是占位符）
        text = self.input_field.text()
        if text:  # 確保輸入框不為空
            language = 'en'
            tts = gTTS(text=text, lang=language, slow=False)
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            # 初始化 pygame 並播放音頻
            pygame.mixer.init()
            pygame.mixer.music.load(audio_fp, 'mp3')
            pygame.mixer.music.play()

            # 防止程序退出，等待播放完成
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
    
 
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('介面應用')

        # Stack Widget 用來管理多個頁面
        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)
        
        # 第一頁
        self.page1 = QLabel(self)
        pixmap1 = QPixmap('image/1.jpg')  # 替換為你的第一張圖片
        self.page1.setPixmap(pixmap1)
        self.page1.setScaledContents(True)
        self.stacked_widget.addWidget(self.page1)
        self.page1.mousePressEvent = self.changePage  # 滑鼠點一下進去大類別頁面
        self.create_buttons_page1()

        # 第二頁 (選大類別頁面)
        self.page2 = QLabel(self)
        pixmap2 = QPixmap('image/2.jpg')  # 替換為你的第二張圖片
        self.page2.setPixmap(pixmap2)
        self.page2.setScaledContents(True)
        self.stacked_widget.addWidget(self.page2)
        self.create_buttons_page2()

        # 第三頁 (自訂頁面)
        self.page3 = CustomPage(self)
        self.page3.back_button.clicked.connect(self.goBackToSecondPage)  # 返回按鈕
        self.stacked_widget.addWidget(self.page3)

        # 第四頁（讀書會與聊聊）
        self.page4 = QLabel(self)
        pixmap4 = QPixmap('image/7.jpg')
        self.page4.setPixmap(pixmap4)
        self.page4.setScaledContents(True)
        self.stacked_widget.addWidget(self.page4)
        self.button_chat_page4 = None  # 確保不重複創建按鈕
        self.button_study_club_page4 = None
        self.page4_back_btn = None

        # 第五頁 (英文練習頁面)
        self.page5 = EnglishPage(self)
        self.page5.back_button.clicked.connect(self.goBackToSecondPage)
        self.stacked_widget.addWidget(self.page5)

        # 第六頁 (統計頁面)
        self.page6 = QLabel(self)
        pixmap6 = QPixmap('image/Statistics.jpg')
        self.page6.setPixmap(pixmap6)
        self.page6.setScaledContents(True)
        self.stacked_widget.addWidget(self.page6)
        self.button_chat_page6 = None
        self.button_study_club_page6 = None
        self.page6_back_btn = None
        # 國文解題頁面
        self.problem_solving_page = ProblemSolvingPage(self)
        self.stacked_widget.addWidget(self.problem_solving_page)
        self.page3.button1.clicked.connect(self.showProblemSolvingPage)

        #註冊介面
        self.signup_page = QLabel(self)
        pixmapsignup = QPixmap('image/account_sing_up_page.jpg')
        self.signup_page.setPixmap(pixmapsignup)
        self.signup_page.setScaledContents(True)
        self.stacked_widget.addWidget(self.signup_page)
        self.createSignupPage()
        #登入介面
        self.signin_page = QLabel(self)
        pixmapsignin = QPixmap('image/account_sing_in_page.jpg')
        self.signin_page.setPixmap(pixmapsignin)
        self.signin_page.setScaledContents(True) # 這裡你可以自訂頁面的內容
        self.stacked_widget.addWidget(self.signin_page)
        self.createSigninPage()

    # 創建按鈕 (第一頁)
    def create_buttons_page1(self):
        width = self.width()
        height = self.height()
        button_width = int(width * 0.130208)
        button_height = int(height * 0.0605)
        
        self.button_chat = QPushButton('sign-up', self.page1)
        self.button_chat.setGeometry(int(width * 0.71354166), int(height * 0.79717457114), int(button_width), int(button_height))
        self.button_chat.clicked.connect(self.showSignupPage)

        self.button_study_club = QPushButton('sign-in', self.page1)
        self.button_study_club.setGeometry(int(width * 0.5625), int(height * 0.79717457114), int(button_width), int(button_height))
        self.button_study_club.clicked.connect(self.showSigninPage)

    # 創建按鈕 (第二頁)
    def create_buttons_page2(self):
        button_positions = [(0.2, 0.3), (0.4, 0.3), (0.7, 0.3), (0.25, 0.6), (0.55, 0.6)]
        self.buttons = []

        for i, pos in enumerate(button_positions):
            btn = QPushButton('', self.page2)
            btn.clicked.connect(lambda checked, idx=i + 1: self.showPage(idx))
            self.buttons.append(btn)

        # 返回按鈕
        back_btn = QPushButton('', self.page2)
        back_btn.setGeometry(0, 0, int(self.width() * 0.06), int(self.height() * 0.074))
        back_btn.clicked.connect(self.goBackToFirstPage)

    def resizeEvent(self, event):
        QMainWindow.resizeEvent(self, event)

        # 調整第二頁按鈕
        width = self.width()
        height = self.height()
        button_width = width * 0.2
        button_height = height * 0.2
        button_positions = [(width * 0.13, height * 0.25), (width * 0.4, height * 0.25), (width * 0.67, height * 0.25),
                            (width * 0.25, height * 0.6), (width * 0.55, height * 0.6)]

        for i, btn in enumerate(self.buttons):
            btn.setGeometry(int(button_positions[i][0]), int(button_positions[i][1]), int(button_width), int(button_height))

        # 調整第四頁與第六頁的按鈕
        self.create_buttons_page4()
        self.create_buttons_page6()

    # 創建按鈕 (第四頁)
    def create_buttons_page4(self):
        width = self.width()
        height = self.height()
        button_width = width * 0.234
        button_height = height * 0.231

        if not self.button_chat_page4:
            self.button_chat_page4 = QPushButton('', self.page4)
        self.button_chat_page4.setGeometry(int(width * 0.6), int(height * 0.509), int(button_width), int(button_height))

        if not self.button_study_club_page4:
            self.button_study_club_page4 = QPushButton('', self.page4)
        self.button_study_club_page4.setGeometry(int(width * 0.156), int(height * 0.509), int(button_width), int(button_height))

        if not self.page4_back_btn:
            self.page4_back_btn = QPushButton('', self.page4)
            self.page4_back_btn.clicked.connect(self.goBackToSecondPage)
        self.page4_back_btn.setGeometry(0, 0, int(width * 0.06), int(height * 0.074))

    # 創建按鈕 (第六頁)
    def create_buttons_page6(self):
        width = self.width()
        height = self.height()
        button_width = width * 0.234
        button_height = height * 0.231

        if not self.button_chat_page6:
            self.button_chat_page6 = QPushButton('', self.page6)
        self.button_chat_page6.setGeometry(int(width * 0.6), int(height * 0.509), int(button_width), int(button_height))

        if not self.button_study_club_page6:
            self.button_study_club_page6 = QPushButton('', self.page6)
        self.button_study_club_page6.setGeometry(int(width * 0.156), int(height * 0.509), int(button_width), int(button_height))

        if not self.page6_back_btn:
            self.page6_back_btn = QPushButton('', self.page6)
            self.page6_back_btn.clicked.connect(self.goBackToSecondPage)
        self.page6_back_btn.setGeometry(0, 0, int(width * 0.06), int(height * 0.074))

    def createSignupPage(self):
        self.signup_username = QLineEdit(self.signup_page)
        self.signup_username.setPlaceholderText("請輸入用戶名")
        self.signup_username.setGeometry(800, 260, 400, 80)  # 手動設置位置

        self.signup_username.setStyleSheet("background: rgba(255, 255, 255, 0.3); border: none; color: black;font-size: 23px;")

        self.signup_account= QLineEdit(self.signup_page)
        self.signup_account.setPlaceholderText("請輸入帳號")
        self.signup_account.setGeometry(800, 385, 400,80) 
        self.signup_account.setStyleSheet("background: rgba(255, 255, 255, 0.3); border: none; color: black;font-size: 23px;")

        self.signup_password = QLineEdit(self.signup_page)
        self.signup_password.setPlaceholderText("請輸入密碼")
        self.signup_password.setGeometry(800, 510, 400,80) 
        self.signup_password.setStyleSheet("background: rgba(255, 255, 255, 0.3); border: none; color:black;font-size: 23px;")
        self.signup_password.setEchoMode(QLineEdit.Password)

        self.signup_button = QPushButton('註冊', self.signup_page)
        self.signup_button.setGeometry(840, 760, 480, 120)

        self.signup_page_back_btn = QPushButton('', self.signup_page)
        self.signup_page_back_btn.clicked.connect(self.goBackToFirstPage)
        self.signup_page_back_btn.setGeometry(0, 0, 120, 100)

        self.signup_button.clicked.connect(self.handleSignup)

    # 登入頁面設置
    def createSigninPage(self):
        self.signin_account = QLineEdit(self.signin_page)
        self.signin_account.setPlaceholderText("請輸入用戶名")
        self.signin_account.setGeometry(800, 245, 400, 80) 
        self.signin_account.setStyleSheet("background: rgba(255, 255, 255, 0.3); border: none; color:black;font-size: 23px;")

        self.signin_password = QLineEdit(self.signin_page)
        self.signin_password.setPlaceholderText("請輸入密碼")
        self.signin_password.setGeometry(800, 385, 400,80)
        self.signin_password.setStyleSheet("background: rgba(255, 255, 255, 0.3); border: none; color: black;font-size: 23px;")
        self.signin_password.setEchoMode(QLineEdit.Password)

        self.signin_button = QPushButton('登入', self.signin_page)
        self.signin_button.setGeometry(840, 760, 480, 120)

        self.signin_page_back_btn = QPushButton('', self.signin_page)
        self.signin_page_back_btn.clicked.connect(self.goBackToFirstPage)
        self.signin_page_back_btn.setGeometry(0, 0, 120, 100)

        self.signin_button.clicked.connect(self.handleSignin)

   # 註冊邏輯
    def handleSignup(self):
        username = self.signup_username.text()
        account = self.signup_account.text()
        password = self.signup_password.text()

        # 調用資料庫註冊功能
        if register_and_login(username, account, password):
            print("註冊並登入成功")
            self.stacked_widget.setCurrentIndex(0)  # 回到首頁或進入應用
        else:
            print("註冊失敗，帳號已存在。")

    # 登入邏輯
    def handleSignin(self):
        account = self.signin_account.text()
        password = self.signin_password.text()

        # 調用資料庫登入檢查功能
        if login_check(account, password):
            print("登入成功")
            self.stacked_widget.setCurrentIndex(0)  # 回到首頁或進入應用
        else:
            print("登入失敗，帳號或密碼錯誤。")


    def showPage(self, button_id):
        if button_id == 1:
            self.stacked_widget.setCurrentIndex(2)
        elif button_id == 5:
            self.stacked_widget.setCurrentIndex(3)
        elif button_id == 3:
            self.stacked_widget.setCurrentIndex(4)
        elif button_id == 4:
            self.stacked_widget.setCurrentIndex(5)

    def goBackToFirstPage(self):
        self.stacked_widget.setCurrentIndex(0)

    def goBackToSecondPage(self):
        self.stacked_widget.setCurrentIndex(1)

    def changePage(self, event):
        self.stacked_widget.setCurrentIndex(1)

    def showProblemSolvingPage(self):
        self.stacked_widget.setCurrentWidget(self.problem_solving_page)

    def showSignupPage(self):
        self.stacked_widget.setCurrentWidget(self.signup_page)

    # 顯示 Sign-in 頁面
    def showSigninPage(self):
        self.stacked_widget.setCurrentWidget(self.signin_page)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.showMaximized()  # 最大化顯示
    sys.exit(app.exec_())
