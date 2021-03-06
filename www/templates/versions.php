<?php defined('ROOT') ? : die('Access denied to '. __FILE__) ?>
<html>
    <head>
        <title>ArGyvers Versions</title>
        <link rel="stylesheet" type="text/css" href="./css/main.css" />
        <link rel="stylesheet" type="text/css" href="./css/versions.css" />
    <head>
    <body>
        <h1><?php echo $item ? $item->name : 'Versions' ?></h1>
<?php if ($item->has_thumbnail()) :?><img src="./thumbnail.php?aid=<?=$aid?>&id=<?=$id?>" alt="<?=$item->name?>" class="thumbnail" /><?php endif ?>
<?php if (empty($versions)) :?>
	<p>No versions found.</p>
<?php else :?>
        <ul>
<?php $v_ = null; foreach ($versions as $v) : ?>
<?php if ($v_ && $v_->get_deleted() != $v->get_created()) : ?>
            <li class="closed">
                <img src="./img/deleted.png" alt="<?=$item->name?>" width="16" height="16" />
                <?= date(LONG_DATE_FORMAT, $v_->get_deleted()) ?>
                <ul><li>deleted</li></ul>
            </li>
<?php endif ?>
<?php if ($v->busy()) : ?>
            <li class="busy">
                <img src="./img/loader.gif" alt="<?=$item->name?>" width="16" height="16" />
                <?= date(LONG_DATE_FORMAT, $v->get_created()) ?>
                <ul><li>busy</li></ul>
            </li>
<?php else : ?>
            <li class="open">
                <a href="./download.php?aid=<?=$aid?>&id=<?=$id?>&vid=<?=$v->id?>" target="_blank" title="Download <?=$item->name?>">
                    <img src="<?= get_icon( $item->is_folder() ? 'folder' : $item->name)?>" alt="<?=$item->name?>" width="16" height="16" />
                    <?= $v->exists() ? '<strong>' : ''?>
                    <?= date(LONG_DATE_FORMAT, $v->get_created()) ?>
                    <ul><li><?= date(DATE_FORMAT, $v->get_mtime()) ?> | <?= date(TIME_FORMAT, $v->get_mtime()) ?> | <?= $v->get_size() ?></li></ul>
                    <?= $v->exists() ? '</strong>' : ''?>
                </a>
            </li>
<?php endif ?>
<?php $v_ = $v; endforeach ?>
<?php if (isset($v) && ! $v->exists()) : ?>
            <li class="closed">
                <img src="./img/deleted.png" alt="<?=$item->name?>" width="16" height="16" />
                <?= date(LONG_DATE_FORMAT, $v_->get_deleted()) ?>
                <ul><li>deleted</li></ul>
            </li>
<?php endif ?>
        </ul>
<?php endif ?>
        <a name="end" />
    </body>
</html>

