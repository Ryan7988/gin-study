from PyQt5.QtGui import QPixmap,  QPainter
from PyQt5.QtWidgets import QLabel,QPushButton,QWidget,QVBoxLayout,QHBoxLayout,QScrollArea,QSpacerItem,QSizePolicy,QTextEdit
from PyQt5.QtCore import Qt, QTimer
from datetime import datetime
import cv2 #新增
import os
import pytesseract #新增
from PIL import Image #新增


#自有
from database.DateBase import insert_gpt,login_check,insert_gpt_message
##全域變數
from GlobalVar import GlobalVar



class TemsolveMainWindow(QWidget):
    def __init__(self,  parent=None, objects=""):
        super().__init__(parent)
        self.parent = parent
        # 設定主視窗
        self.setWindowTitle("Chat Window Example")
        self.setAttribute(Qt.WA_TranslucentBackground, True)  # 設置整體透明
        #self.showFullScreen()  # 設置為全螢幕
        self.resize(800, 480)  # 設定視窗大小為 800x600

        # 設定背景圖片
        if (objects == "國文"):
            self.background_image_path = 'Window/image/chinese.jpg'
        elif (objects == "數學"):
            self.background_image_path = 'Window/image/math.jpg'
        elif (objects == "自然"):
            self.background_image_path = 'Window/image/science.jpg'
        elif (objects == "英文"):
            self.background_image_path = 'Window/image/english.jpg'
        elif (objects == "社會"):
            self.background_image_path = 'Window/image/social.jpg'
        else:
            self.background_image_path = 'Window/image/psychological.jpg'
            
        

        # 主佈局
        main_layout = QVBoxLayout(self)
        # 上方返回按鈕 (透明)
        top_layout = QHBoxLayout()
        self.back_button = QPushButton("")
        self.back_button.setFixedSize(50, 50)
        self.back_button.setStyleSheet("background-color: rgba(, 0, 0, 1);")
        top_layout.addWidget(self.back_button)
        top_layout.setAlignment(Qt.AlignLeft)
        main_layout.addLayout(top_layout)

        # 添加獨立的滾動區域
        self.scroll_area = self.create_scroll_area()
        main_layout.addWidget(self.scroll_area)

        # 底部輸入區域
        input_layout = QHBoxLayout()

        # 相機按鈕 (透明)
        camera_button = QPushButton("相機")
        camera_button.setFixedSize(50, 50)
        camera_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        input_layout.addWidget(camera_button)

        # 輸入框 (多行輸入)
        self.input_field = QTextEdit()
        self.input_field.setFixedHeight(50)
        self.input_field.setStyleSheet("""
            border-radius: 25px;
            padding-left: 20px;
            background-color: rgba(200, 200, 200, 0.5);
        """)
        self.input_field.setPlaceholderText("Type a message...")
        self.input_field.setMaximumHeight(40)  # 設置最大高度
        self.input_field.textChanged.connect(
            self.adjust_input_height)  # 根據文字調整高度
        input_layout.addWidget(self.input_field)

        # 傳送按鈕 (透明)
        send_button = QPushButton("傳送")
        send_button.setFixedSize(50, 50)
        send_button.setStyleSheet("background-color: rgba(0, 0, 0, 0);")
        # send_button.clicked.connect(self.add_message(objects))
        send_button.clicked.connect(lambda: self.add_message(objects))
        input_layout.addWidget(send_button)

        main_layout.addLayout(input_layout)
    
    def capture_photo(self,objects):
        # 使用 OpenCV 啟動攝像頭
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("無法開啟攝像頭")
            return

        ret, frame = cap.read()
        if ret:
            # 將照片保存到本地
            file_path = 'Window/menu/CustomPage/captured_image.jpg'
            cv2.imwrite(file_path, frame)
            
            # 使用 Tesseract OCR 進行文字識別
            question_text = self.extract_text_from_image(file_path)
            self.input_field.setText(question_text)  # 將識別出的文字設置到輸入框
            
            self.add_message(objects)  # 傳遞給 GPT 進行解答

        cap.release()

    def extract_text_from_image(self, image_path):
        # 使用 Tesseract OCR 識別文字
        os.chdir('Window/menu/CustomPage/Tesseract-OCR/tessdata')
        pytesseract.pytesseract.tesseract_cmd = 'Window/menu/CustomPage/Tesseract-OCR/tesseract.exe'
        try:
            image = Image.open('Window/menu/CustomPage/captured_image.jpg')
            text = pytesseract.image_to_string(image, lang='chi_tra')  # 以繁體中文模式辨識
            print(text)
            return text

        except Exception as e:
            print(f"OCR 識別錯誤: {e}")
            return "無法識別文字"
    def paintEvent(self, event):
        # 使用 QPainter 繪製背景圖片
        painter = QPainter(self)
        pixmap = QPixmap(self.background_image_path)
        painter.drawPixmap(self.rect(), pixmap)
    
    def create_scroll_area(self):
        # 建立滾動區域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet(
            "background-color: rgba(0, 0, 0, 0);")  # 透明背景

        # 聊天內容Widget
        self.chat_content = QWidget()
        self.chat_content.setStyleSheet(
            "background-color: rgba(0, 0, 0, 0);")  # 透明背景
        self.chat_layout = QVBoxLayout(self.chat_content)
        self.chat_layout.setContentsMargins(10, 10, 10, 10)
        self.chat_layout.setSpacing(10)

        # 添加頂部空白區域
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum,
                             QSizePolicy.Expanding)
        self.chat_layout.addItem(spacer)

        scroll_area.setWidget(self.chat_content)
        return scroll_area

    def adjust_input_height(self):
        # 根據輸入文字的高度動態調整輸入框的高度
        document_height = int(self.input_field.document().size().height())
        self.input_field.setFixedHeight(
            min(document_height + 10, 100))  # 調整最大高度到 150
        # 確保文字可以換行顯示
    


    def add_message(self, objects):
        # 取得輸入的文字並清空輸入框
        message = self.input_field.toPlainText()
        # 把使用者輸入的問題傳進對話框
        # 這是把問的問題丟入gpt 幹您娘
        
        
        current_date = datetime.now()
        GlobalVar.gpt_id = insert_gpt(objects, current_date.strftime("%Y-%m-%d"), GlobalVar.uID)

        insert_gpt_message(GlobalVar.gpt_id, message, True)
        self.input_field.clear()

        if message:
            # 用戶訊息顯示（靠右）
            user_message_layout = QHBoxLayout()
            user_message_layout.setAlignment(Qt.AlignRight)  # 對齊到右側

            # 頭貼部分
            user_avatar = QLabel()
            user_avatar.setPixmap(
                self.create_circle_avatar("Window/image/0.jpg"))  # 用戶頭貼
            user_avatar.setFixedSize(50, 50)  # 設定頭貼大小
            user_avatar.setScaledContents(True)  # 圖片自動縮放

            # 設定用戶的輸入框
            user_message_label = QLabel(message)
            user_message_label.setStyleSheet("""
                background-color: #dcf8c6; 
                border-radius: 20px; 
                padding: 10px; 
                word-wrap: break-word;
                max-width: 300px;  /* 限制最大寬度 */
            """)
            user_message_label.setSizePolicy(
                QSizePolicy.Minimum, QSizePolicy.Minimum)
            user_message_label.setWordWrap(True)  # 啟用自動換行

            user_message_layout.addWidget(user_message_label)  # 用戶訊息在頭貼右側
            user_message_layout.addWidget(user_avatar)  # 頭貼放在右邊
            self.chat_layout.addLayout(user_message_layout)

            # 對方的回答顯示（靠左）
            response_message_layout = QHBoxLayout()
            response_message_layout.setAlignment(Qt.AlignLeft)  # 對齊到左側

            # 頭貼部分
            bot_avatar = QLabel()
            bot_avatar.setPixmap(
                self.create_circle_avatar("Window/image/0.jpg"))  # 機器人頭貼
            bot_avatar.setFixedSize(50, 50)  # 設定頭貼大小
            bot_avatar.setScaledContents(True)  # 圖片自動縮放
            response = self.solve_problem(message, objects)
            # 這是回復
            insert_gpt_message(GlobalVar.gpt_id, response, False)
            # 設定對方的回答

            response_message_label = QLabel(response)
            response_message_label.setStyleSheet("""
                background-color: #f1f0f0; 
                border-radius: 20px; 
                padding: 10px; 
                word-wrap: break-word; 
                max-width: 300px;  /* 限制最大寬度 */
            """)
            response_message_label.setSizePolicy(
                QSizePolicy.Minimum, QSizePolicy.Minimum)
            response_message_label.setWordWrap(True)  # 啟用自動換行

            response_message_layout.addWidget(bot_avatar)  # 頭貼放在左邊
            response_message_layout.addWidget(
                response_message_label)  # 機器人回答在頭貼右側
            self.chat_layout.addLayout(response_message_layout)

            # 滾動條位置設定
            QTimer.singleShot(10, lambda: self.scroll_area.verticalScrollBar().setValue(
                self.scroll_area.verticalScrollBar().maximum()))

    def gpt_35_api_stream(self, messages: list):  # GPT 輸出
        try:
            stream = GlobalVar.client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=messages,
                stream=True,
            )
            full_response = ""
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content  # 輸出
            return full_response
        except Exception as e:
            #self.answer_label.setText(f"發生錯誤: {e}")
            return f"發生錯誤: {e}"

    def solve_problem(self, question, objects):
        if question:
            # 構造發送給 GPT 的訊息
            if (objects == "國文"):
                messages = [
                    {'role': 'user', 'content': f'你是個國小和國中的國文老師，麻煩用繁體中文幫她解決問題，問題是「{question}」'}]
            elif (objects == "數學"):
                messages = [
                    {'role': 'user', 'content': f'你是個國小和國中的數學老師，麻煩用繁體中文幫她解決問題，問題是「{question}」'}]
            elif (objects == "自然"):
                messages = [
                    {'role': 'user', 'content': f'你是個國小和國中的自然老師，麻煩用繁體中文幫她解決問題，問題是「{question}」'}]
            elif (objects == "英文"):
                messages = [
                    {'role': 'user', 'content': f'你是個國小和國中的英文老師，麻煩用繁體中文幫她解決問題，問題是「{question}」'}]
            elif (objects == "社會"):
                messages = [
                    {'role': 'user', 'content': f'你是個國小和國中的社會老師，麻煩用繁體中文幫她解決問題，問題是「{question}」'}]
            elif (objects == "與...聊聊"):
                messages = [
                    {'role': 'user', 'content': f'你是個國小和國中的心理諮商老師，，會有學生來找你傾訴他的煩惱，請你給予他正確且安全的反饋和建議，請你勁量表現得像個人，可以是老師或朋友，麻煩用繁體中文，他想說的是「{question}」'}] 
            print(messages)

            # 調用 GPT API 生成解答
            response = self.gpt_35_api_stream(messages)
            return response

    def create_circle_avatar(self, image_path):
        # 生成圓形頭貼
        pixmap = QPixmap(image_path)
        size = min(pixmap.width(), pixmap.height())
        pixmap = pixmap.scaled(size, size)
        mask = pixmap.createMaskFromColor(Qt.transparent)
        pixmap.setMask(mask)
        return pixmap