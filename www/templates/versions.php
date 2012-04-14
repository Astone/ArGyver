<?php defined('ROOT') ? : die('Access denied to '. __FILE__) ?>
<html>
    <head>
        <title>ArGyvers Versions</title>
        <link rel="stylesheet" type="text/css" href="./css/main.css" />
        <link rel="stylesheet" type="text/css" href="./css/versions.css" />
    <head>
    <body>
        <h1><? echo $path ? $path->name : 'Versions' ?></h1>
<?php foreach ($versions as $v) : ?>
    <li><a href="./download.php?aid=<?=$aid?>&pid=<?=$pid?>&vid=<?=$v->id?>" target="_blank"><?= date('d-m-Y', $v->get_time()) ?></a></li>
<?php endforeach ?>
    </body>
</html>

