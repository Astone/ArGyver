<?php defined('ROOT') ? : die('Access denied to '. __FILE__) ?>
<html>
    <head>
        <title>ArGyvers Versions</title>
        <link rel="stylesheet" type="text/css" href="./css/main.css" />
        <link rel="stylesheet" type="text/css" href="./css/versions.css" />
    <head>
    <body>
        <h1><?php echo $path ? $path->name : 'Versions' ?></h1>
<?php echo $path ? '<p>Click to download:</p>' : '' ?>
<?php $v_ = null; foreach ($versions as $v) : ?>
<?php if ($v_ && $v_->get_deleted() != $v->get_created()) : ?>
            <li class="closed"><?= date('d-m-Y', $v_->get_deleted()) ?> <small>(deleted)</small></a></li>
<?php endif ?>
<?php if ($pid) : ?>
            <li class="open"><a href="./download.php?aid=<?=$aid?>&pid=<?=$pid?>&vid=<?=$v->id?>" target="_blank" title="download"><?= date('d-m-Y', $v->get_created()) ?> <small>(<?= date('d-m-Y H:i:s', $v->get_mtime()) ?>)</small></a></li>
<?php else : ?>
            <li class="open"><a href="./download.php?aid=<?=$aid?>&fid=<?=$fid?>&iid=<?=$v->id?>" target="_blank" title="download"><?= date('d-m-Y', $v->get_created()) ?> <small>(<?= date('d-m-Y H:i:s', $v->get_mtime()) ?>)</small></a></li>
<?php endif?>
<?php $v_ = $v; endforeach ?>
<?php if (! $v->is_open()) : ?>
            <li class="closed"><?= date('d-m-Y', $v->get_deleted()) ?> <small>(deleted)</small></a></li>
<?php endif ?>
    </body>
</html>

