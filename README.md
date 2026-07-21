# QuizOut
QuizOut is a python solution hosting Jeopardy-style trivia games with a physical buzzer. I wrote this software to aid in hosting trivia games between 2 teams of 3 players each (but player count and teams are configurable). To give the players physical buzzers, I bought a 6-key keyboard from [techkeys.us](https://techkeys.us) and soldered extension wires with 3d-printed handles onto the keyboard so that each player could have his own buzzer. The buzzers follow the famous Jeopardy rule, where players who buzz in before the host has activated the buzzers will have their buzzers deactivated for a short time.

## Server/Client Architecture

Quizout is broken into a server and a client. They can be run on the same computer or separately. For my purposes, I ran the server on a Windows laptop and the client on a Raspberry Pi 4.

The server hosts a web page where admins can activate the buzzers and see which player buzzed in first.

The client is a pyqt desktop application that handles the keyboard input and sound effects. The client treats keyboard keys as individual buzzers for each player. The keys are configurable via a config.ini file (see [quizout-client/config.ini.example](./quizout-client/config.ini.example).)

## Project layout
Both server and client are included in this repo with their respective directories and corresponding requirements.txt files. Use these to create separate venv's for each.

## Server Notes

### Setup
First, create a .env file in the quizout-server directory. The contents should look like the following:

```
# .env file
SECRET_LOCATION=~/.quizoutserver/secrets/
SQLITE_PATH=~/.quizoutserver/db/db.sqlite
DEBUG=True
```

`SECRET_LOCATION` should point to a directory where you store your keys as text files. Permissions for this location should be modified so that only the user running the server has access. (For dev purposes, this user account can be your account.) The secret directory should contain the following files:
 - api_key
 - api_secret
 - db_pass

These should each contain your desired secret.

`SQLITE_PATH` should point to where you want the server to store its sqlite DB. The db file will be created the first time you run the application, so there is no need to create the file yourself.

### Docker
For running the server in production, the Dockerfile is set up to run the server with gunicorn. The quickest way to get it up and running is to use docker compose (i.e., navigate to the server directory and run `$ docker compose up -d`).

## Client Notes

### Raspberry Pi Setup for Global Key Capture

When running the client on Raspberry Pi (Raspbian), additional setup is required for global keyboard capture to work without sudo:

#### 1. Add your user to the input group:
First, add your user to the 'input' group:

```bash
sudo usermod -a -G input $USER
```

#### 2. Create udev rules for keyboard device access:

Next, identify your keyboard devices:

```bash
cat /proc/bus/input/devices | grep -A 5 -B 5 "Name="
```

Look for keyboard devices you would like to use to and note their vendor/product IDs (idVendor and idProduct).

Then create a udev rule:
```bash
sudo tee /etc/udev/rules.d/99-keyboard-access.rules << 'EOF'
# Replace VENDOR_ID and PRODUCT_ID with your keyboard's actual IDs
SUBSYSTEM=="input", ATTRS{idVendor}=="VENDOR_ID", ATTRS{idProduct}=="PRODUCT_ID", KERNEL=="event*", ENV{ID_INPUT_KEYBOARD}=="1", GROUP="input", MODE="0664"

# Alternative: Match by device name (replace "Your Keyboard Name" with actual name)
SUBSYSTEM=="input", ATTRS{name}=="Your Keyboard Name", KERNEL=="event*", ENV{ID_INPUT_KEYBOARD}=="1", GROUP="input", MODE="0664"
EOF
```

#### 3. Apply the changes:
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

#### 4. Log out and log back in (or reboot):
```bash
sudo reboot
```

After completing these steps, the client should be able to capture global keyboard events without requiring sudo privileges.

**Note**: The `ENV{ID_INPUT_KEYBOARD}=="1"` condition ensures only actual keyboard devices are affected, preventing interference with other input devices like mice or GPU devices.

## Sound Credits
Many thanks to the following users on freesound.org for creating the sound effects used in this project:
 - [rhodesmas](https://freesound.org/people/rhodesmas/)
 - [metalfortress](https://freesound.org/people/metalfortress/)
 - [etheraudio](https://freesound.org/people/etheraudio/)