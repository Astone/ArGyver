<?php defined('ROOT') ? : die('Access denied to '. __FILE__) ?>
<html>
    <head>
        <title>ArGyvers Folders</title>
        <link rel="stylesheet" type="text/css" href="./css/main.css" />
        <link rel="stylesheet" type="text/css" href="./css/folders.css" />
    <head>
    <body>
        <a href="./?aid=<?= $aid ?>" title="<?=$archive->name?>" target="_top"><h1><img src="./img/archive.png" alt="<?=$archive->name?>" /> <?=$archive->name?></h1></a>
        <ul class="folders">
<?php foreach ($parents as $p) : ?>
            <li class="<?php echo $p->exists() ? "open" : "closed" ?>">
                <a href="./?aid=<?= $aid ?>&fid=<?= $p->id ?>&id=<?= $p->id ?>" target="_top">
                    <img src="<?= get_icon('folder_open')?>" alt="<?=$p->name?>" width="16" height="16" />
                    <?=str_replace(' ', '&nbsp;', htmlentities($p->name))?>
                </a>
                <ul>
<?php endforeach ?>
<?php foreach ($siblings as $s) : ?>
                    <li class="<?php echo ($fid == $s->id) ? 'current ' : '' ?><?php echo $s->exists() ? 'open' : 'closed' ?>">
                        <a name="f<?=$s->id?>" />
                        <a href="./?aid=<?= $aid ?>&fid=<?= $s->id ?>&id=<?= $s->id ?>" target="_top">
                            <img src="<?= get_icon($fid == $s->id ? 'folder_open' : 'folder')?>" alt="<?=$s->name?>" width="16" height="16" />
                            <?=str_replace(' ', '&nbsp;', htmlentities($s->name))?>
                        </a>
<?php if ($fid == $s->id) :?>
                        <ul>
<?php foreach ($children as $c) : ?>
                            <li class="<?php echo $c->exists() ? 'open' : 'closed' ?>">
                                <a href="./?aid=<?= $aid ?>&fid=<?= $c->id ?>&id=<?= $c->id ?>" target="_top">
                                <img src="<?= get_icon('folder')?>" alt="<?=$c->name?>" width="16" height="16" />
                                <?=str_replace(' ', '&nbsp;', htmlentities($c->name))?>
                                </a>
                            </li>
<?php endforeach ?>
                        </ul>
<?php endif ?>
                    </li>
<?php endforeach ?>
<?php for($i = 0; $i < sizeof($parents); $i++) : ?>
                </ul>
            </li>
<?php endfor ?>
        </ul>
    </body>
</html>

