import QtQuick
import QtQuick.Controls

Window {
    id: root
    width: 800
    height: 600
    visible: true
    title: qsTr("Hello World")

    property alias connectEnabled: connectButton.enabled
    property alias disconnectEnabled: disconnectButton.enabled

    Column {
        spacing: 4
        anchors.fill: parent
        anchors.margins: 10

        Button {
            id: connectButton
            text: qsTr("Connect to Server")
            onClicked: mainWindow.on_connect_click()
        }

        Button {
            id: disconnectButton
            text: qsTr("Disconnect from Server")
            enabled: false
            onClicked: mainWindow.on_disconnect_click()
        }

        Row {
            spacing: 2
            ComboBox {
                id: soundEffectCombo
                model: [
                    { text: qsTr("Activate"), value: 0 },
                    { text: qsTr("Buzz"), value: 1 },
                    { text: qsTr("Correct"), value: 2 },
                    { text: qsTr("Incorrect"), value: 3 },
                    { text: qsTr("Timeout"), value: 4 }
                ]
                textRole: "text"
                valueRole: "value"
            }
            Button {
                id: testSoundButton
                text: "\u25B6 Test Sound"
                onClicked: mainWindow.on_test_sound_click(soundEffectCombo.currentIndex)
            }
        }
    }

    onClosing: mainWindow.on_close()
}
