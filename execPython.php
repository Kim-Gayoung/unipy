<?php
    $pyfile = '실행해야되는 MyCloud.py 파일 경로';
    $pyexec = 'python.exe 경로';

    $pyarg = "";
    
    foreach ($_POST as $key => $value) {
        $pyarg .= "\"$value\"";
        $pyarg .= " ";
    }

    $cmd = "$pyexec $pyfile $pyarg";

    print shell_exec($cmd);
?>