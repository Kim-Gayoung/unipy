## 1. How to Run Unipy Program

  Download the Unipy program from the following address.
  (https://github.com/Kim-Gayoung/unipy)

  You can run the Unipy program as follow, and select the case.

  ```
  C:\ > python UnipyPrgram.py
  1: door state, 2: control, 3: DB content, 4: total case, 5: custom case
  Enter the number : _
  ```

  > <p style="height:10px;">The first case is what the door open/close state is saved in the DB when the door opened and closed.</p>
  > <p style="height:10px;">The second case is to control the servo motor attaching to the camera.</p>
  > <p style="height:10px;">The third case is to check the open/close state of the door stored in the DB.</p>
  > <p style="height:10px;">The fourth case is the sum of case from 1 to 3.</p>
  > <p style="height:20px;">The final case is the option to run the case you wrote.</p>


## 2. Setting up Each Device
### 2-1. Arduino
- Arduino Board
  Arduino Uno


- Arduino Parts
  Magnetic Door Sensor(MC-38)
  Micro Servo Motor(SG-90)


- Arduino Parts Wiring
  * Magnetic Door Sensor Wiring
    One of the Magnetic Door Sensor Wire is connected with Arduino Digital Pin 2.
    The other is connected with Arduino GND.

  * Micro Servo Motor Wiring
    Brown wire of servo motor is connected with Arduino GND.
    Red wire is connected with Arduino 5V, and Orange wire is connected with Arduino Digital Pin 10.


### 2-2. Raspberry Pi
- Raspberry Pi Board
  Raspberry Pi 3 Model B

- Raspberry Pi OS version
  2017-03-02-raspbian-jessie

- Raspberry Pi Configuration
  > Advanced Options > Expand Filesystem > Yes

  > Interfacing Options > Camera > Yes
  > Interfacing Options > SSH > Yes
  > Interfacing Options > VNC > Yes

- Installed Program in Raspberry Pi
  * Arduino IDE
  `sudo apt-get install arduino`

  * UV4L(in jessie version)
  After executing commands as follows:
  `curl http://www.linux-projects.org/listing/uv4l_repo/lrkey.asc | sudo apt-key add -`

  And add the following content `/etc/apt/sources.list` file.
  `deb http://www.linux-projects.org/listing/uv4l_repo/raspbian/ jessie main`

  And execute commands as follows:
  ```
  sudo apt-get update
  sudo apt-get install uv4l uv4l_raspicam
  sudo apt-get install uv4l-raspicam-extras

  sudo service uv4l_raspicam restart
  ```

  **Other versions can install this library referencing 'http://www.linux-projects.org/uv4l/installation/'**

- Python Version
  Python 3.6

- Libraries used in Python
  > urllib3(1.9.1)
  > pyserial(2.6)

  You can install these libraries as following commands:
  `pip install urllib3`
  `pip install pyserial`

### 2-3. Cloud
- Python 3.6 Installation
  Click the 'Lastest Python 3 Release - Python 3.6.4' in this https://www.python.org/downloads/windows/.
  And execute the downloaded installer as an administrator privilege.

  Check in the bottom check box and Click 'Install Now'.
  > Install launcher for all users(recommended) : When checked, All users can use Python without administrator privilege. When unchecked, All users except administrator need administrator privilege when running Python.
  > Add Python 3.6 to PATH : When checked, this Installer will automatically add Python installation path to PATH. When unchecked, user should add the Python installation path to PATH.

- PHP7 Installation
  Download PHP archive according to your computer specification at http://windows.php.net/download/.