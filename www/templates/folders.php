<?php defined('ROOT') ? : die('Access denied to '. __FILE__) ?>
<html>
    <head>
        <title>ArGyvers Folders</title>
        <link rel="stylesheet" type="text/css" href="./css/main.css" />
        <link rel="stylesheet" type="text/css" href="./css/folders.css" />
    <head>
    <body>
        <h1>Folders</h1>
        <?php echo get_tree(get('cid'), get('fid')) ?>
    </body>
</html>

