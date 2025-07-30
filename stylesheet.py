STYLE_SHEET = """
QWidget {
    background-color: #2b2b2b;
    font-family: 'Segoe UI', 'Malgun Gothic', sans-serif;
    font-size: 14px;
    color: #eeeeee;
}

QPushButton {
    background-color: #3c3c3c;
    border: 1px solid #555555;
    border-radius: 12px;
    padding: 8px 16px;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #4a4a4a;
}

QPushButton:disabled {
    background-color: #2a2a2a;
    border: 1px solid #444444;
    color: #777777;
}

QLineEdit, QTextEdit {
    background-color: #333333;
    border: 1px solid #555555;
    border-radius: 8px;
    padding: 6px 10px;
    font-weight: normal;
    color: #ffffff;
}

QLabel {
    color: #dddddd;
    font-weight: normal;
}

QGroupBox {
    border: 1px solid #555555;
    border-radius: 10px;
    margin-top: 15px;
    font-weight: bold;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    color: #eeeeee;
    font-weight: bold;
}

QScrollBar:vertical {
    background: white;
    width: 12px;
    margin: 0px 0px 0px 0px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background: #555555;
    min-height: 20px;
    border-radius: 6px;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    background: gray;
    border-radius: 6px;
}

"""
