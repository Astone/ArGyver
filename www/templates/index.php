<?php defined('ROOT') ? : die('Access denied') ?>
<html>
    <head>
        <title>ArGyver v3.1 alpha</title>
    <head>
    <frameset rows="120,*,60">
        <frame src="./header.php<?=$cid.$vid?>" name="header" />
        <frameset cols="240,*,240">
            <frame src="./folders.php<?=$cid.$fid.$flink?>" name="folders" />
            <frame src="./files.php<?=$cid.$fid.$plink?>" name="files" />
            <frame src="./versions.php<?=$cid.$pid.$vlink?>" name="versions" />
        </frameset>     
        <frame src="./footer.php<?=$cid.$vid?>" name="footer" />
    </frameset>
</html>

