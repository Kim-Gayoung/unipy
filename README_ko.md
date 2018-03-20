## 1. Unipy 프로그램 사용 방법

  아래 주소에서 unipy 프로그램을 다운로드 받는다.
  (https://github.com/Kim-Gayoung/unipy)
   
  Unipy 프로그램을 아래와 같이 실행할 수 있으며, 케이스를 선택할 수 있다.
  
  ``` 
  C:\ > python UnipyProgram.py
  1: door state, 2: control, 3: DB content, 4: total case, 5: custom case
  Enter the number : _
  ```

> <p style="height:20px">1번은 문이 열리고 닫히는 것을 DB에 저장하는 케이스</p>
> <p style="height:20px">2번은 카메라가 달려있는 서보모터를 회전시키는 케이스</p>
> <p style="height:20px">3번은 DB에 저장된 문의 여닫힘 정보를 확인하는 케이스</p>
> <p style="height:20px">4번은 1번부터 3번까지를 합친 케이스</p>
> <p style="height:20px">5번은 사용자가 작성한 케이스를 실행할 수 있는 선택사항이다.</p>


   
## 2. 각 디바이스 설정
### 2-1. Arduino
- Arduino Board<br>
  Arduino Uno


- Arduino Parts<br>
  마그네틱 도어 센서(MC-38)<br>
  마이크로 서보 모터(SG-90)


- Arduino Parts Wiring
	* 마그네틱 도어 센서 연결<br>
		마그네틱 도어 센서의 선 중 하나를 아두이노 디지털 핀 2번에 연결한다.<br>
		다른 선은 아두이노 GND에 연결한다.
			
	* 마이크로 서보 모터 연결<br>
		서보모터의 갈색 선은 아두이노 GND에 연결한다.<br>
		빨간 선은 아두이노의 5V에 연결하며, 주황색선은 아두이노 디지털 핀 10번에 연결한다.<br>

   
### 2-2. Raspberry Pi
- Raspberry Pi Board<br>
	Raspberry Pi 3 Model B
		  
- Raspberry Pi OS version<br>
	2017-03-02-raspbian-jessie
		
- Raspberry Pi 설정
	> Advanced Options > Expand Filesystem > Yes

	> Interfacing Options > Camera > Yes<br>
	> Interfacing Options > SSH > Yes<br>
	> Interfacing Options > VNC > Yes<br>
		
- Raspberry Pi 설치된 프로그램
	* Arduino IDE<br>
	`sudo apt-get install arduino`
		
	* UV4L(in jessie version)<br>
		`curl http://www.linux-projects.org/listing/uv4l_repo/lrkey.asc | sudo apt-key add -` 명령어를 실행한 후에
			
		`/etc/apt/sources.list` 파일에 아래 내용을 추가한다<br>
		`deb http://www.linux-projects.org/listing/uv4l_repo/raspbian/ jessie main`

		파일의 변경된 내용을 저장한 후 다음과 같은 명령어를 실행한다.<br>
		```
        sudo apt-get update
		sudo apt-get install uv4l uv4l_raspicam
		sudo apt-get install uv4l-raspicam-extras
        
		sudo service uv4l_raspicam restart
        ```
			
		**다른 버전들은 'http://www.linux-projects.org/uv4l/installation/' 주소를 참고하여 설치하면 된다.**
		

- Python Version<br>
	Python 3.6
		

- Libraries used in Python<br>
  > urllib3(1.9.1)<br>
  > pyserial(2.6)

  pip 명령어를 이용하여 위와 같은 라이브러리를 설치할 수 있다.<br>
  `pip install _`


### 2-3. Cloud
- Python 3.6 설치<br>
	https://www.python.org/downloads/windows/ 에서 Lastest Python 3 Release - Python 3.6.4를 클릭한다.<br>
	다운로드 받은 인스톨러를 관리자 권한으로 실행한다.<br>

	하단의 체크박스를 모두 체크하고 `Install Now`를 클릭<br>
	> Install launcher for all users(recommended) : 체크 시 모든 사용자가 파이썬 사용 가능, 체크 해제 시 파이썬 실행시 관리자 권한 필요<br>
	> Add Python 3.6 to PATH : 체크 시 PATH에 자동으로 파이썬 설치 경로를 추가해줌, 체크 해제 시 PATH에 사용자가 파이썬 설치 경로를 추가해야함


- PHP7 설치<br>
	http://windows.php.net/download/ 에서 자신의 사양에 맞는 php 압축파일 다운로드(Php 7 사용)<br>
	다운로드 된 압축파일(zip) 해제<br>
	압축 해제된 파일의 php.ini-development 파일을 복사 및 파일명을 php.ini로 변경<br>
	  
	php.ini를 열어 다음과 같은 내용을 수정 및 저장<br>
	`extendsion_dir = "php7 경로"`<br>
		  
- Apache 설치<br>
	http://apachelounge.com/download/ 에서 자신의 사양에 맞는 apache 압축파일 다운로드(Apache2.4 사용)<br>
	다운로드된 압축파일(zip) 해제<br>
	압축 해제된 파일의 conf에 가면 httpd.conf 파일 존재 및 수정<br>
	  
	PHP 이용을 위해 모듈 로드 추가(httpd.conf 파일 하단)
	```
    LoadModule php7_module "php7apache2_4.dll 경로"
	PHPInDir "php 경로"
	SetHandler application/x-httpd-php
    ```
		  
	수정된 httpd.conf 내용을 저장하고, 서비스를 추가하고 실행하기 위해 cmd를 관리자 모드로 실행<br>
	아파치 파일의 bin 파일로 이동 후 다음 명령어 실행<br>
	`httpd.exe -k install`(httpd 서비스 설치)<br>
	`httpd.exe -k start`(httpd 서비스 실행)
  * **php 연동 확인하는 방법**<br>
	  아파치 파일의 htdocs 파일내에 phpinfo.php라는 파일명으로 아래 내용을 저장<br>
		`<?php phpinfo(); ?>`<br>
	  http://localhost/phpinfo.php에 php 버전 정보들이 출력된다면 연동완료
		
- MySQL 설치<br>
	http://dev.mysql.com/download/mysql/ 에서 MySQL Community Server를 다운로드 받는다.<br>
	다운로드 된 압축파일 해제<br>
	  
	cmd를 관리자 모드로 실행하여 압축해제한 MySQL의 bin 폴더로 이동<br>
	`mysqld --install` 명령어 입력<br>
		  
	설치 후 제어판 -> 관리도구 -> 서비스 에서 mysql 서비스 시작<br>
		  
	php와 연동을 위해 php의 php.ini 파일 수정(;로 주석처리 -> ; 제거)<br>
	`extension = php_mysqli.dll`

	저장 후 제어판 -> 관리도구 -> 서비스 에서 apache 재실행


- DB 스키마 정보<br>
	MySQL에 테이블을 추가한다. 다음과 같은 쿼리문을 이용하면 된다.<br>
	```
	CREATE TABLE doorlist(d_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    			d_openclose VARCHAR(10) NOT NULL,
    			d_pic_loc VARCHAR(200) NOT NULL,
                          PRIMARY KEY(t_time));
	```
- PHP Program
	다운로드한 unipy의 execPython.php 파일을 아파치의 htdocs로 이동
		  
	<pre><code>$pyfile = "실행할 파이썬 파일 경로";
	$pyexec = "파이썬 실행파일 경로";</code></pre>


### 2-4. Mobile/Desktop
python을 실행할 수 있는 환경 구축(2-3의 python 설치 참고)

## 3. Compilation and Deployment each device program
### 3-1. Arduino
Arduino IDE에 MyArduino.ino를 복사해서 컴파일 및 업로드

		
### 3-2. Raspberry Pi
라즈베리 파이의 Python 스크립트에 MyRaspberry.py를 복사, 저장 및 실행

		
### 3-3. Mobile/Desktop
PC에서 MyMobile.py를 실행한 후, 첫 시작이 되는 함수인 main() 호출

   
### 3-4. Cloud
2-3의 PHP Program에 따라 실행이 필요한 python 파일을 MyCloud.py의 경로로 변경 및 저장
   

## 4. How to run Mobile/Desktop Program
사용자의 입력을 통해 반복 실행할 수 있는 코드를 작성해야 하며, 다음과 같이 작성할 수 있다.
```
def selectCommand():
  while True:
	  print ("[1]: show door state, [2]: delete door state")
	  select = input("Select Command :")

	  if select == '1':
		  showDoorList()
	  elif select == '2':
		  deleteDoorList()
 .
 .
 .
selectCommand()
```
