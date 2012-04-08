<?php defined('security_check') ? : die('Access denied') ?>
<html>
    <head>
        <title>ArGyvers Folders</title>
        <link rel="stylesheet" href="css/main.css" />
        <link rel="stylesheet" href="css/folders.css" />
    <head>
    <body>
        <h1>Archives</h1>
        <?php echo get_tree(get('cid'), get('fid')) ?>
    </body>
</html>

