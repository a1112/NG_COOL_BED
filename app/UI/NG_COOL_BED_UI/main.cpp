#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QIcon>
#include <QByteArray>

int main(int argc, char *argv[])
{
    qputenv("QT_FFMPEG_LOGLEVEL", QByteArray("error"));
    QGuiApplication app(argc, argv);
    // app.setWindowIcon(QIcon(":/icons/app_icon.png"));
    QQmlApplicationEngine engine;
    QObject::connect(
        &engine,
        &QQmlApplicationEngine::objectCreationFailed,
        &app,
        []() { QCoreApplication::exit(-1); },
        Qt::QueuedConnection);
    engine.load(QUrl(u"qrc:/qt/qml/NG_COOL_BED_UI/Main.qml"_qs));

    return app.exec();
}
