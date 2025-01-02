import cv2
import math
import mediapipe as mp
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QPushButton, QMessageBox, QHBoxLayout
from datetime import datetime, timedelta

# 自有
from database.DateBase import insert_focus_time, login_check
# 全域變數
from GlobalVar import GlobalVar

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    update_concern_value_signal = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self._run_flag = True
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False, max_num_faces=1, refine_landmarks=True,
            min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.cap = cv2.VideoCapture(0)
        self.eye_ratio_threshold = 0.6
        self.mouth_ratio_threshold = 1.0
        self.eyes_average = 0
        self.mouth_average = 0
        self.concern_value = 0.0
        self.data_count = 0
        self.data_max = 50
                # 創建返回按鈕
        width=800
        height=480
        self.back_button = QPushButton('', self)
        self.back_button.setGeometry(
            0, 0, int(width*0.06), int(height*0.0807265))

    def run(self):
        while self._run_flag:
            ret, frame = self.cap.read()
            if ret:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = self.face_mesh.process(frame_rgb)
                if results.multi_face_landmarks:
                    for face_landmarks in results.multi_face_landmarks:
                        eye_ratio = self.calculate_eye_ratio(face_landmarks)
                        mouth_ratio = self.calculate_mouth_ratio(face_landmarks)
                        self.Average_judgify(face_landmarks, eye_ratio, mouth_ratio)
                        self.valueJudgment(eye_ratio, mouth_ratio)
                        self.update_concern_value_signal.emit(self.concern_value)

                        for landmark in face_landmarks.landmark:
                            x = int(landmark.x * frame.shape[1])
                            y = int(landmark.y * frame.shape[0])
                            cv2.circle(frame_rgb, (x, y), 1, (0, 255, 0), -1)

                h, w, ch = frame_rgb.shape
                bytes_per_line = ch * w
                qt_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.change_pixmap_signal.emit(qt_img)

    def calculate_eye_ratio(self, face_landmarks):
        left_eye_ratio = self.calc_distance(face_landmarks, 145, 159) / self.calc_distance(face_landmarks, 33, 133)
        right_eye_ratio = self.calc_distance(face_landmarks, 374, 386) / self.calc_distance(face_landmarks, 263, 362)
        return (left_eye_ratio + right_eye_ratio) / 2

    def calculate_mouth_ratio(self, face_landmarks):
        return self.calc_distance(face_landmarks, 13, 14) / self.calc_distance(face_landmarks, 308, 78)

    def calc_distance(self, face_landmarks, idx1, idx2):
        point1 = face_landmarks.landmark[idx1]
        point2 = face_landmarks.landmark[idx2]
        return math.sqrt((point1.x - point2.x) ** 2 + (point1.y - point2.y) ** 2)

    def Average_judgify(self, face_landmarks, eye_value, mouth_value):
        if self.data_count < self.data_max:
            self.eyes_average = self.eyes_average * (self.data_count / (self.data_count + 1)) + eye_value / (self.data_count + 1)
            self.mouth_average = self.mouth_average * (self.data_count / (self.data_count + 1)) + mouth_value / (self.data_count + 1)
            self.data_count += 1

    def valueJudgment(self, eye_ratio, mouth_ratio):
        eye_value = eye_ratio / self.eyes_average if self.eyes_average else 0
        mouth_value = mouth_ratio / self.mouth_average if self.mouth_average else 0
        self.valueCalculator(eye_value, mouth_value)

    def valueCalculator(self, eye_value, mouth_value):
        weight_eyes = 0.7
        weight_mouth = 0.3
        self.concern_value = eye_value * weight_eyes + (2 - mouth_value) * weight_mouth

    def stop(self):
        self._run_flag = False
        self.cap.release()
        self.wait()

class FocusDetectionPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("專注度監測")
        self.resize(1280, 720)
        self.selected_subject = None  # 儲存選擇的科目

        # 設定背景圖片
        self.background_label = QLabel(self)
        self.background_pixmap = QPixmap("Window/image/blue.jpg")
        self.background_label.setPixmap(self.background_pixmap)
        self.background_label.setScaledContents(True)  # 自動縮放背景圖片
        self.background_label.setGeometry(0, 0, self.width(), self.height())  # 設置為全屏
        self.background_label.lower()  # 確保背景圖片在最底層

        # 設置其他組件
        self.camera_label = QLabel(self)
        self.camera_label.setFixedSize(800, 600)  # 加大攝像頭畫面

        self.concern_value_label = QLabel("專注度: 0.0", self)
        self.concern_value_label.setStyleSheet("font-size: 30px;")  # 增加字體大小
        self.timer_label = QLabel("計時: 0 s", self)
        self.timer_label.setStyleSheet("font-size: 30px;")  # 增加字體大小

        # 設置水平的開始計時和停止計時按鈕
        self.start_button = QPushButton("開始計時", self)
        self.start_button.setFixedSize(200, 100)  # 增大按鈕
        self.start_button.setStyleSheet("border-radius: 10px; background-color: #ADD8E6; font-size: 30px;")
        self.start_button.clicked.connect(self.start_timer)

        self.stop_button = QPushButton("停止計時", self)
        self.stop_button.setFixedSize(200, 100)  # 增大按鈕
        self.stop_button.setStyleSheet("border-radius: 10px; background-color: #FFB6C1; font-size: 30px;")
        self.stop_button.clicked.connect(self.stop_timer)

        # 科目選擇按鈕
        self.subject_buttons = {
            "國文": QPushButton("國文", self),
            "英文": QPushButton("英文", self),
            "數學": QPushButton("數學", self),
            "社會": QPushButton("社會", self),
            "自然": QPushButton("自然", self)
        }

        for subject, button in self.subject_buttons.items():
            button.setFixedSize(80, 40)
            button.clicked.connect(lambda _, s=subject: self.select_subject(s))

        # 主佈局
        main_layout = QVBoxLayout()
        
        # 中心化攝像頭畫面
        camera_layout = QHBoxLayout()
        camera_layout.addStretch(1)
        camera_layout.addWidget(self.camera_label)
        camera_layout.addStretch(1)
        main_layout.addLayout(camera_layout)

        # 專注度與計時器並列顯示
        info_layout = QHBoxLayout()
        info_layout.addWidget(self.concern_value_label, alignment=Qt.AlignCenter)
        info_layout.addWidget(self.timer_label, alignment=Qt.AlignCenter)
        main_layout.addLayout(info_layout)

        # 水平佈局的開始和停止按鈕
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        main_layout.addLayout(button_layout)

        # 科目按鈕佈局
        subject_layout = QHBoxLayout()
        for button in self.subject_buttons.values():
            subject_layout.addWidget(button, alignment=Qt.AlignRight)
        main_layout.addLayout(subject_layout)

        # 配置主窗口
        container_widget = QWidget(self)
        container_widget.setLayout(main_layout)
        container_widget.setGeometry(0, 0, self.width(), self.height())
        self.setLayout(main_layout)

        # 初始化計時和執行緒
        self.elapsed_time = 0
        self.is_timing = False
        self.display_timer = QTimer(self)
        self.display_timer.timeout.connect(self.update_elapsed_time)

        # 攝像頭執行緒
        self.thread = VideoThread()
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.update_concern_value_signal.connect(self.update_concern_value)
        self.thread.start()

        self.focus_warning_shown = False

        

    # 動態調整背景圖片的大小
    def resizeEvent(self, event):
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        super(FocusDetectionPage, self).resizeEvent(event)
        self.back_button.setGeometry(
            0, 0, int(800*0.055), int(480*0.0807265))

    # 選擇科目
    def select_subject(self, subject):
        self.selected_subject = subject
        QMessageBox.information(self, "科目選擇", f"您已選擇科目：{subject}")

    def start_timer(self):
        if not self.selected_subject:
            QMessageBox.warning(self, "未選擇科目", "請先選擇科目再開始計時。")
            return
        if not self.is_timing:
            QMessageBox.information(self, "計時開始", f"您選擇的科目為：{self.selected_subject}")
            self.is_timing = True
            self.elapsed_time = 0
            self.display_timer.start(1000)
            self.timer_label.setText("計時: 0 s")

    def stop_timer(self):
        if self.is_timing:
            self.is_timing = False
            self.display_timer.stop()
            
            # 將專注時間記錄到資料庫
            current_date = datetime.now()
            focus_time = str(timedelta(seconds=self.elapsed_time))
            focus_time = focus_time.zfill(8)  # 補足到 8 位格式
            # 將專注時間插入資料庫
            insert_focus_time(GlobalVar.uID, current_date.strftime("%Y-%m-%d"), focus_time)
            print(GlobalVar.uID)
            print(current_date.strftime("%Y-%m-%d"))
            print(focus_time)

            print(f"已儲存專注時間：{focus_time} 給用戶 {GlobalVar.uID}")

    def update_elapsed_time(self):
        if self.is_timing:
            self.elapsed_time += 1
            self.timer_label.setText(f"計時: {self.elapsed_time} s")

    def update_image(self, qt_img):
        self.camera_label.setPixmap(QPixmap.fromImage(qt_img))

    def update_concern_value(self, concern_value):
        self.concern_value_label.setText(f"專注度: {concern_value:.2f}")
        if concern_value < 0.7 and self.is_timing and not self.focus_warning_shown:
            self.stop_timer()
            self.focus_warning_shown = True
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("不專心提醒")
            msg.setText("您的專注度低於 1.0，請專心！")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.buttonClicked.connect(self.reset_focus_warning)
            msg.exec_()

    def reset_focus_warning(self):
        self.focus_warning_shown = False

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()


