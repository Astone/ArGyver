<?php defined('ROOT') ? : die('Access denied') ?>
<html>
    <head>
        <title>ArGyver v3.1 beta</title>
    <head>
    <frameset rows="100,*" >
        <frame src="./archives.php<?=$aid?>" name="archives" />
        <frameset cols="240,*,240">
            <frame src="./folders.php<?=$aid.$fid.$flink?>" name="folders" />
            <frame src="./files.php<?=$aid.$fid.$id.$ilink?>" name="files" />
            <frame src="./versions.php<?=$aid.$id?>" name="versions" />
        </frameset>
    </frameset>
</html>

