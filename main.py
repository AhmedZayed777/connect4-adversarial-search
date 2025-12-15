import sys
from PySide6.QtWidgets import QApplication
from guiMM import MainMenu  # استيراد من الملف الجديد

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # تحسين مظهر التطبيق
    app.setStyle("Fusion")
    
    # إعدادات إضافية للأناقة
    from PySide6.QtGui import QFont
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = MainMenu()
    
    # تعيين أيقونة للتطبيق (اختياري)
    # from PySide6.QtGui import QIcon
    # window.setWindowIcon(QIcon("assets/images/icon.png"))
    
    # Show main menu fullscreen by default
    window.showFullScreen()
    
    sys.exit(app.exec())