from PyQt5.QtWidgets import QMainWindow, QStackedWidget, QLabel, QPushButton, QLineEdit, QWidget, QMessageBox
from PyQt5.QtGui import QPixmap

# 自訂
from Window.menu.CustomPage.CustomPage import CustomPage
from Window.menu.StatisticsPage.AnalysisPage.SubjectAnalysisPage import SubjectAnalysisPage
from Window.menu.CustomPage.TemsolveMainWindow import TemsolveMainWindow
from Window.menu.StatisticsPage.AnalysisPage.AnalysisPage import AnalysisPage
from Window.menu.EnglishPage.EnglishPage import EnglishPage
from Window.menu.ClubPage.ClubTablePage import ClubTable
from Window.menu.Focus.focus import FocusDetectionPage  # 導入專注偵測頁面
from database.DateBase import register_and_login, login_check, find_gpt, get_name_by_uid, select_family_request, agree_family_request
from GlobalVar import GlobalVar
from Window.menu.StatisticsPage.AnalysisPage.FocusAnalysisPage import FocusAnalysisPage

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('介面應用')
        self.setFixedSize(800, 480)  # 固定主視窗大小為 800x480
        #print(f"\n\n\nMain window size: {self.size()}\n\n\n")  # 固定主視窗大小為 800x480
        # Stack Widget 用來管理多個頁面
        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)
        self.page_index_map = {}

        # 第一頁(首頁)
        self.MainPage = QLabel(self)
        pixmap1 = QPixmap('Window/image/1.jpg')
        self.MainPage.setPixmap(pixmap1)
        self.MainPage.setScaledContents(True)
        self.MainPage.setFixedSize(800, 480)
        self.addStackedWidget_updatePageIndexMap("首頁", self.MainPage)
        self.create_buttons_MainPage()

        # 第二頁 (主菜單)
        self.MenuPage = MENUPAGE()
        pixmap2 = QPixmap('Window/image/2.jpg')
        self.MenuPage.setPixmap(pixmap2)
        self.MenuPage.setScaledContents(True)
        self.MenuPage.setFixedSize(800, 480)
        self.addStackedWidget_updatePageIndexMap("主菜單", self.MenuPage)
        self.create_buttons_MenuPage()

        # 第三頁 (解題科目菜單)
        self.GPTMenuPage = CustomPage(self)
        self.GPTMenuPage.setFixedSize(800, 480)
        self.GPTMenuPage.back_button.clicked.connect(lambda _, Page="主菜單": self.showPage(Page))
        self.addStackedWidget_updatePageIndexMap("解題", self.GPTMenuPage)

        # 第四頁（讀書會）
        self.ClubPage = QLabel(self)
        pixmap4 = QPixmap('Window/image/7.jpg')
        self.ClubPage.setPixmap(pixmap4)
        self.ClubPage.setScaledContents(True)
        self.ClubPage.setFixedSize(800, 480)
        self.ClubPage.back_button.clicked.connect(lambda _, Page="主菜單": self.showPage(Page))
        self.addStackedWidget_updatePageIndexMap("讀書會", self.ClubPage)
        self.create_buttons_ClubPage()

        # 第五頁 (英文練習頁面)
        self.EnglishPage = EnglishPage(self)
        self.EnglishPage.setFixedSize(800, 480)
        self.EnglishPage.back_button.clicked.connect(lambda _, Page="主菜單": self.showPage(Page))
        self.addStackedWidget_updatePageIndexMap("英文翻譯", self.EnglishPage)

        # 第六頁 (統計頁面)
        self.StatisticsPage = QLabel(self)
        pixmap6 = QPixmap('Window/image/Statistics.jpg')
        self.StatisticsPage.setPixmap(pixmap6)
        self.StatisticsPage.setScaledContents(True)
        self.StatisticsPage.setFixedSize(800, 480)
        self.addStackedWidget_updatePageIndexMap("統計", self.StatisticsPage)
        self.create_buttons_StatisticsPage()

        # 第七頁 (專注偵測)
        self.FocusDetectionPage = FocusDetectionPage(self)
        self.FocusDetectionPage.setFixedSize(800, 480)
        self.FocusDetectionPage.back_button.clicked.connect(lambda _, Page="主菜單": self.showPage(Page))
        self.addStackedWidget_updatePageIndexMap("專注偵測", self.FocusDetectionPage)

        # 分析頁面
        self.analysis_page = AnalysisPage(self)
        self.analysis_page.setFixedSize(800, 480)
        self.analysis_page.back_button.clicked.connect(lambda _, Page="統計": self.showPage(Page))
        self.addStackedWidget_updatePageIndexMap("分析", self.analysis_page)

        # 專注分析
        self.focus_analysis_page = FocusAnalysisPage(self)
        self.focus_analysis_page.setFixedSize(800, 480)
        self.addStackedWidget_updatePageIndexMap("專注分析", self.focus_analysis_page)

        # 初始化各個分析頁面
        subject_name = ["國文", "數學", "英文", "自然", "社會"]
        self.SubjectAnalysisPage_map = {}
        for subject in subject_name:
            self.SubjectAnalysisPage_map[subject + "分析"] = SubjectAnalysisPage(subject, self)
            self.SubjectAnalysisPage_map[subject + "分析"].setFixedSize(800, 480)
            back_btn = QPushButton('', self.SubjectAnalysisPage_map[subject + "分析"])
            back_btn.setGeometry(0, 0, int(800 * 0.06), int(480 * 0.074))
            back_btn.clicked.connect(lambda _, Page="分析": self.showPage(Page))
            self.addStackedWidget_updatePageIndexMap(subject + "分析", self.SubjectAnalysisPage_map[subject + "分析"])

        # 初始化解題頁面
        self.INFO_solving_page()

        # 註冊與登入頁面
        self.init_auth_pages()

    def create_buttons_MainPage(self):
        width, height = 800, 480
        button_width = int(width * 0.15)
        button_height = int(height * 0.08)

        # 登入按鈕 - 放置在右下角偏右的位置
        self.button_signup = QPushButton('Sign-Up', self.MainPage)
        self.button_signup.setGeometry(int(width * 0.7), int(height * 0.79), button_width, button_height)

        # 註冊按鈕 - 放置在右下角偏左的位置
        self.button_signin = QPushButton('Sign-In', self.MainPage)
        self.button_signin.setGeometry(int(width * 0.55), int(height * 0.79), button_width, button_height)

        self.button_signup.clicked.connect(lambda _, Page="註冊": self.showPage(Page))
        self.button_signin.clicked.connect(lambda _, Page="登入": self.showPage(Page))

    # def create_buttons_MenuPage(self):
    #     button_names = ["解題", "專注偵測", "英文翻譯", "統計", "讀書會"]
    #     self.buttons = []
    #     for i, name in enumerate(button_names):
    #         btn = QPushButton(name, self.MenuPage)
    #         btn.setGeometry(100 + i * 120, 200, 100, 50)
    #         btn.clicked.connect(lambda _, Page=name: self.showPage(Page))
    #         self.buttons.append(btn)
    def create_buttons_MenuPage(self):
    # 按鈕名稱
        button_names = ["解題", "專注偵測", "英文翻譯", "統計", "讀書會"]

        # 自定義每個按鈕的位置和大小 (x, y, width, height)
        button_positions = [
            (100, 110, 170, 130),  # 解題
            (315, 110, 170, 130),  # 專注偵測
            (530, 110, 170, 130),  # 英文翻譯
            (205, 280, 170, 125),  # 統計
            (420, 280, 170, 125)   # 讀書會
        ]

        self.buttons = []
        for i, name in enumerate(button_names):
            btn = QPushButton(name, self.MenuPage)
            # 設置按鈕的位置和大小
            btn.setGeometry(*button_positions[i])
            # 設置按鈕的點擊事件
            btn.clicked.connect(lambda _, Page=name: self.showPage(Page))
            self.buttons.append(btn)


    def create_buttons_ClubPage(self):
        self.button_club_chart = QPushButton('讀書會圖表', self.ClubPage)
        self.button_club_chart.setGeometry(200, 300, 150, 50)
        self.button_club_chart.clicked.connect(lambda _, Page="讀書會圖表": self.showPage(Page))

        self.button_club_chat = QPushButton('與...聊聊', self.ClubPage)
        self.button_club_chat.setGeometry(400, 300, 150, 50)
        self.button_club_chat.clicked.connect(lambda _, Page="與...聊聊": self.showPage(Page))

    def create_buttons_StatisticsPage(self):
        self.button_focus_analysis = QPushButton('專注分析', self.StatisticsPage)
        self.button_focus_analysis.setGeometry(200, 300, 150, 50)
        self.button_focus_analysis.clicked.connect(lambda: self.showPage("專注分析"))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.resize(800, 480)  # 強制調整視窗大小為 800x480

    def showPage(self, title: str):
        if title in self.page_index_map:
            self.stacked_widget.setCurrentIndex(self.page_index_map[title])
        else:
            print(f'頁面展示失敗: {title}')

    def addStackedWidget_updatePageIndexMap(self, name: str, page: QWidget):
        self.stacked_widget.addWidget(page)
        index = self.stacked_widget.indexOf(page)
        self.page_index_map[name] = index

    def INFO_solving_page(self):
        subject_names = ["國文", "數學", "英文", "自然", "社會"]
        for subject in subject_names:
            subject_page = TemsolveMainWindow(self, subject)
            subject_page.setFixedSize(800, 480)
            self.addStackedWidget_updatePageIndexMap(subject + "解題", subject_page)
            self.GPTMenuPage.button_map[subject].clicked.connect(lambda _, Page=subject + "解題": self.showPage(Page))
            subject_page.back_button.clicked.connect(lambda _, Page="解題": self.showPage(Page))

    def init_auth_pages(self):
        # 註冊頁面
        self.signup_page = QLabel(self)
        pixmap_signup = QPixmap('Window/image/account_sing_up_page.jpg')
        self.signup_page.setPixmap(pixmap_signup)
        self.signup_page.setScaledContents(True)
        self.signup_page.setFixedSize(800, 480)
        self.addStackedWidget_updatePageIndexMap("註冊", self.signup_page)
        self.createSignupPage()

        # 登入頁面
        self.signin_page = QLabel(self)
        pixmap_signin = QPixmap('Window/image/account_sing_in_page.jpg')
        self.signin_page.setPixmap(pixmap_signin)
        self.signin_page.setScaledContents(True)
        self.signin_page.setFixedSize(800, 480)
        self.addStackedWidget_updatePageIndexMap("登入", self.signin_page)
        self.createSigninPage()

    def createSignupPage(self):
        self.signup_username = QLineEdit(self.signup_page)
        self.signup_username.setPlaceholderText("請輸入用戶名")
        self.signup_username.setGeometry(345, 110, 250, 40)

        self.signup_account = QLineEdit(self.signup_page)
        self.signup_account.setPlaceholderText("請輸入帳號")
        self.signup_account.setGeometry(345, 180, 250, 40)

        self.signup_password = QLineEdit(self.signup_page)
        self.signup_password.setPlaceholderText("請輸入密碼")
        self.signup_password.setGeometry(345, 250, 250, 40)
        self.signup_password.setEchoMode(QLineEdit.Password)

        self.signup_button = QPushButton('註冊', self.signup_page)
        self.signup_button.setGeometry(360, 360, 180, 85)
        self.signup_button.clicked.connect(self.handleSignup)

    def createSigninPage(self):
        self.signin_account = QLineEdit(self.signin_page)
        self.signin_account.setPlaceholderText("請輸入帳號")
        self.signin_account.setGeometry(340, 110, 250, 40)

        self.signin_password = QLineEdit(self.signin_page)
        self.signin_password.setPlaceholderText("請輸入密碼")
        self.signin_password.setGeometry(345, 180, 250, 40)
        self.signin_password.setEchoMode(QLineEdit.Password)

        self.signin_button = QPushButton('登入', self.signin_page)
        self.signin_button.setGeometry(360, 360, 180, 85)
        self.signin_button.clicked.connect(self.handleSignin)

    def handleSignup(self):
        username = self.signup_username.text()
        account = self.signup_account.text()
        password = self.signup_password.text()
        user = register_and_login(username, account, password)
        if user.uID > 0:
            print(f"註冊成功！用戶名: {username}")
            GlobalVar.uID = user.uID
            self.showPage("主菜單")
        else:
            print("註冊失敗，可能帳號已存在。")

    def handleSignin(self):
        account = self.signin_account.text()
        password = self.signin_password.text()
        user = login_check(account, password)
        if user.uID > 0:
            print(f"登入成功！用戶名: {user.name}, 用戶ID: {user.uID}")
            GlobalVar.uID = user.uID
            GlobalVar.gpt_data = find_gpt(user.uID)
            self.showPage("主菜單")
        else:
            print("登入失敗，用戶名或密碼錯誤。")

class MENUPAGE(QLabel):
    def __init__(self):
        super().__init__()
        self.setFixedSize(800, 480)

    def showEvent(self, event):
        super().showEvent(event)
        requests = select_family_request(GlobalVar.uID)
        requests = requests.get("received_requests", [])

        for parentID, _ in requests:
            dialog = QMessageBox(
                icon=QMessageBox.Question,
                text=f'是否同意來自 {get_name_by_uid(parentID)} (uID: {parentID}) 成為你的父母的請求'
            )
            dialog.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            choice = dialog.exec()
            agree_family_request(parentID, GlobalVar.uID, 1 if choice == QMessageBox.Yes else 0)
