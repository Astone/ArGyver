<?php defined('ROOT') ? : die('Access denied to '. __FILE__) ?>
<html>
    <head>
        <title>ArGyvers Folders</title>
        <link rel="stylesheet" type="text/css" href="./css/main.css" />
        <link rel="stylesheet" type="text/css" href="./css/folders.css" />
        <script src="javascript/folders.js" language="JavaScript"></script>
    <head>
    <body onload="load(<?php echo get('cid', 0) ?>, <?php echo get('fid', 0) ?>);">
        <h1>Archives</h1>
        <?php echo get_tree(get('cid'), get('fid')) ?>
    </body>
</html>

