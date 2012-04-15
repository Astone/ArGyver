<?php defined('ROOT') ? : die('Access denied to '. __FILE__) ?>
<html>
    <head>
        <title>ArGyvers Calculating Folder Size</title>
        <link rel="stylesheet" type="text/css" href="./css/main.css" />
        <script src="./js/files.js" language="JavaScript"></script>
    <head>
    <body onload="countdown(<?=$timeout?>); redirect('./calculate_size.php?aid=<?=$aid?>&fid=<?=$fid?>')">
        <h1><?php echo $folder->name ?></h1>
        <p>Calculating the size of "<?php echo $folder->name ?>": <b><?=$size?></b> so far . . . <span id="timer"><?= $timeout ?></span></p>
    </body>
</html>

