<?php defined('security_check') ? : die('Access denied') ?>
<html>
    <head>
        <title>ArGyver v3.1 alpha</title>
    <head>
    <frameset rows="120,*,60">
        <frame src="header.php" name="header" />
        <frameset cols="240,*,240">
            <frame src="folders.php" name="folders" />
            <frame src="files.php" name="files" />
            <frame src="versions.php" name="versions" />
        </frameset>     
        <frame src="footer.php" name="footer" />
    </frameset>
</html>

