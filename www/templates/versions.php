<?php defined('ROOT') ? : die('Access denied to '. __FILE__) ?>
<html>
    <head>
        <title>ArGyvers Versions</title>
        <link rel="stylesheet" type="text/css" href="./css/main.css" />
        <link rel="stylesheet" type="text/css" href="./css/versions.css" />
    <head>
    <body>
        <h1><?php echo $item ? $item->name : 'Versions' ?></h1>
<?php echo $item ? '<p>Click to download:</p>' : '' ?>
        <ul>
<?php $v_ = null; foreach ($versions as $v) : ?>
<?php if ($v_ && $v_->get_deleted() != $v->get_created()) : ?>
            <li class="closed">
                <img src="<?= get_icon('deleted')?>" alt="<?=$item->name?>" width="16" height="16" />
                <?= date(LONG_DATE_FORMAT, $v_->get_deleted()) ?>
                <ul><li>deleted</li></ul>
            </li>
<?php endif ?>
            <li class="open">
                <a href="./download.php?aid=<?=$aid?>&id=<?=$id?>&vid=<?=$v->id?>" target="_blank" title="download" <?php echo ($v->get_size(false) >= LARGE_FILE_SIZE) ? "onclick=\"return download(\"$item->name\", \"".$item->get_size()."\", ".($item->is_folder()?'true':'false').")" : '' ?>>
                    <img src="<?= get_icon( $item->is_folder() ? 'folder' : $item->name)?>" alt="<?=$item->name?>" width="16" height="16" />
                    <?= date(LONG_DATE_FORMAT, $v->get_created()) ?>
                    <ul><li><?= date(DATE_FORMAT, $v->get_mtime()) ?> | <?= date(TIME_FORMAT, $v->get_mtime()) ?> | <?= $v->get_size() ?></li></ul>
                </a>
            </li>
<?php $v_ = $v; endforeach ?>
<?php if (! $v->exists()) : ?>
            <li class="closed">
                <img src="<?= get_icon('deleted')?>" alt="<?=$item->name?>" width="16" height="16" />
                <?= date(LONG_DATE_FORMAT, $v_->get_deleted()) ?>
                <ul><li>deleted</li></ul>
            </li>
<?php endif ?>
        </ul>
    </body>
</html>

