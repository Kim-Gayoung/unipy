## 1. How to Run Unipy Program

  Download the Unipy program from the following address.<br>
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
- Arduino Board<br>
  Arduino Uno

- Arduino Parts<br>
  Magnetic Door Sensor(MC-38)<br>
  Micro Servo Motor(SG-90)


- Arduino Parts Wiring
  * Magnetic Door Sensor Wiring<br>
    One of the Magnetic Door Sensor Wire is connected with Arduino Digital Pin 2.<br>
    The other is connected with Arduino GND.

  * Micro Servo Motor Wiring<br>
    Brown wire of servo motor is connected with Arduino GND.<br>
    Red wire is connected with Arduino 5V, and Orange wire is connected with Arduino Digital Pin 10.


### 2-2. Raspberry Pi
- Raspberry Pi Board<br>
  Raspberry Pi 3 Model B

- Raspberry Pi OS version<br>
  2017-03-02-raspbian-jessie

- Raspberry Pi Configuration<br>
  > Advanced Options > Expand Filesystem > Yes

  > Interfacing Options > Camera > Yes<br>
  > Interfacing Options > SSH > Yes<br>
  > Interfacing Options > VNC > Yes<br>

- Installed Program in Raspberry Pi
  * Arduino IDE<br>
  `sudo apt-get install arduino`

  * UV4L(in jessie version)<br>
  After executing commands as follows:<br>
  `curl http://www.linux-projects.org/listing/uv4l_repo/lrkey.asc | sudo apt-key add -`

  And add the following content `/etc/apt/sources.list` file.<br>
  `deb http://www.linux-projects.org/listing/uv4l_repo/raspbian/ jessie main`

  And execute commands as follows:
  ```
  sudo apt-get update
  sudo apt-get install uv4l uv4l_raspicam
  sudo apt-get install uv4l-raspicam-extras

  sudo service uv4l_raspicam restart
  ```

  **Other versions can install this library referencing 'http://www.linux-projects.org/uv4l/installation/'**

- Python Version<br>
  Python 3.6

- Libraries used in Python
  > urllib3(1.9.1)<br>
  > pyserial(2.6)

  You can install these libraries as following commands:<br>
  `pip install urllib3`<br>
  `pip install pyserial`<br>

### 2-3. Cloud
- Python 3.6 Installation<br>
  Click the 'Lastest Python 3 Release - Python 3.6.4' in this https://www.python.org/downloads/windows/.<br>
  And execute the downloaded installer as an administrator permission.

  Check in the bottom check box and Click 'Install Now'.
  > Install launcher for all users(recommended) : When checked, All users can use Python without administrator permission. When unchecked, All users except administrator need administrator permission when running Python.<br>
  > Add Python 3.6 to PATH : When checked, this Installer will automatically add Python installation path to PATH. When unchecked, user should add the Python installation path to PATH.

- PHP7 Installation<br>
  Download PHP archive according to your computer specification at http://windows.php.net/download/.<br>
  Unzip the downloaded PHP archive.<br>
  Copy the 'php.ini-development' file  and modify this file name to 'php.ini'.<br>
  And open the 'php.ini' file and modify content as follows:<br>
  `extendsion_dir = "php7 installation path"`<br>

- Apache Installation<br>
  Download Apache archive according to your computer specification at http://apachelounge.com/download/.<br>
  Unzip the downloaded Apache archive.<br>
  Modify the 'httpd.conf' file in the 'conf' directory.<br>

  Add the module load to use PHP.<br>
  Add the content as follows:
  ```
  LoadModule php7_module "php7apache2_4.dll path"
  PHPInDir "php7 installation path"
  SetHandler application/x-httpd-php
  ```

  Save the modified 'httpd.conf' content and execute cmd as administrator permission to add and run the Apache service.<br>
  Move 'bin' file in Apache directory and execute the commands as follows:<br>
  `httpd.exe -k install`(Install httpd service)<br>
  `httpd.exe -k start`(Start httpd service)<br>

  * **The way of checking that PHP and Apache work together**<br>
    In the htdocs directory of Apache, save the following content to the 'phpinfo.php' file.<br>
    `<?php phpinfo(); ?>`<br>
    If you can see the PHP information at http://localhost/phpinfo.php, PHP is well connected to Apache.<br>

- MySQL Installation<br>
  Download the MySQL Community Server archive at http://dev.mysql.com/download/mysql/.<br>
  Unzip the downloaded MySQL Community Server archive.<br>

  Execute cmd as administrator permission and Move the 'bin' directory in the MySQL.<br>
  And execute `mysqld --install` command.<br>

  After installation, start the MySQL service at `Control Panel -> Administrative Tool -> Services`.<br>

  Modify 'php.ini' file in PHP installation directory to connect PHP and MySQL together.<br>
  Find the following commented text and delete ';' in front of it.<br>
  `extension = php_mysqli.dll`

  Save the modified file and restart Apache service at `Control Panel -> Administrative Tool -> Services`.

- Information about DB schema<br>
  Add MySQL table. And execute query as follows:
  ```
  CREATE TABLE doorlist(d_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
      d_openclose VARCHAR(10) NOT NULL,
      d_pic_loc VARCHAR(200) NOT NULL,
      PRIMARY KEY(d_time))
  ```

- PHP Program to execute Python File
  Move 'execPython.php' file in the downloaded Unipy to htdocs in Apache.
  ```
  $pyfile = "python file path to execute";
  $pyexec = "Python execute file path";
  ```

### 2-4. Mobile/Desktop
Build an environment to execute Python(Reference 2-3 python installation)

## 3. Compilation and Deployment Each Device Program
### 3-1. Arduino
You can copy and paste 'MyArudino.ino' file contents to Arduino IDE.<br>
And you can compile and upload it through Arduino IDE.<br>

### 3-2. Raspberry Pi
You can copy and paste 'MyRaspberry.py' contents to Python Script at Raspberry Pi.
you can save and execute it.

### 3-3. Mobile/Desktop
After Executing 'MyMobile.py' file on your PC, you need to call the main() function that is the first start.

### 3-4. Cloud
You need to modify and save the 'execPython.php' in htdocs directory according to the '2-3. PHP Program' section.

## 4. How to run Mobile/Desktop Program
You should write repeately executable program through users input