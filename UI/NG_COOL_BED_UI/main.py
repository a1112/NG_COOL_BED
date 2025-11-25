"""
Launch the QML UI with PySide6.

Usage:
    python main.py
"""

import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine


def main() -> int:
    app = QGuiApplication(sys.argv)
    app.setApplicationName("NG_COOL_BED_UI")
    app.setOrganizationName("NG_COOL_BED")

    base_dir = Path(__file__).resolve().parent
    qml_file = base_dir / "Main.qml"

    # 优先尝试加载编译好的资源（需先运行 pyside6-rcc qml.qrc -o qml_rc.py）
    use_qrc = False
    try:
        import qml_rc  # type: ignore  # noqa: F401
        use_qrc = True
    except ImportError:
        use_qrc = False

    engine = QQmlApplicationEngine()

    if use_qrc:
        url = QUrl("qrc:/qt/qml/NG_COOL_BED_UI/Main.qml")
    else:
        # 直接从文件系统加载，并补充 import 路径
        engine.addImportPath(str(base_dir))
        engine.addImportPath(str(base_dir / "qml"))
        url = QUrl.fromLocalFile(str(qml_file))

    engine.load(url)
    if not engine.rootObjects():
        return -1

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
