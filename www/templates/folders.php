<?php defined('ROOT') ? : die('Access denied to '. __FILE__) ?>
<html>
    <head>
        <title>ArGyvers Folders</title>
        <link rel="stylesheet" type="text/css" href="./css/main.css" />
        <link rel="stylesheet" type="text/css" href="./css/folders.css" />
    <head>
    <body>
        <h1><?= $archive->name ?></h1>
        <ul class="folders">
<?php foreach ($parents as $p) : ?>
            <li><a href="./?aid=<?= $aid ?>&fid=<?= $p->id ?>" target="_top"><?= $p->name ?></a>
                <ul>
<?php endforeach ?>
<?php foreach ($siblings as $s) : ?>
<?php if ($fid == $s->id) :?>
                    <li class="current"><a name="f<?=$s->id?>" /><a href="./?aid=<?= $aid ?>&fid=<?= $s->id ?>" target="_top"><?= $s->name ?></a>
                        <ul>
<?php foreach ($children as $c) : ?>
                            <li><a href="./?aid=<?= $aid ?>&fid=<?= $c->id ?>" target="_top"><?= $c->name ?></a></li>
<?php endforeach ?>
                        </ul>
<?php else : ?>
                    <li><a href="./?aid=<?= $aid ?>&fid=<?= $s->id ?>" target="_top"><?= $s->name ?></a></li>
<?php endif ?>
<?php endforeach ?>
<?php for($i = 0; $i < sizeof($parents); $i++) : ?>
                </ul>
            </li>
<?php endfor ?>
        </ul>
    </body>
</html>

