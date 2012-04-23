<?php defined('ROOT') ? : die('Access denied to '. __FILE__) ?>
<html>
    <head>
        <title>ArGyvers Header</title>
        <link rel="stylesheet" type="text/css" href="./css/main.css" />
        <link rel="stylesheet" type="text/css" href="./css/archives.css" />
    <head>
    <body>
<?php if ($archive && $archive->db_exists()): ?>
    <form action="./" target="_top" method="GET" style="float:right">
    <input type="hidden" name="aid" value="<?=$aid?>" />
    <input type="hidden" name="fid" value="<?=$fid?>" />
    <input type="hidden" name="id" value="<?=$id?>" />
    Time window:
    <select name="min_vid">
<?php foreach ($archive->get_iterations() as $v) : ?>
        <option value="<?=$v['id']?>" <? if ($v['id'] == MIN_V) echo 'selected'?>><?= date(DATE_FORMAT.' ('.TIME_FORMAT.')', $v['start']) ?></option>
<?php endforeach ?>
    </select>
    -
    <select name="max_vid">
<?php foreach ($archive->get_iterations() as $v) : ?>
        <option value="<?=$v['id']?>" <? if ($v['id'] == MAX_V) echo 'selected'?>><?= date(DATE_FORMAT.' ('.TIME_FORMAT.')', $v['start']) ?></option>
<?php endforeach ?>
    </select>
    <input type="submit" value="Go" />
    </form>
<?php endif ?>
        <h1>ArGyver v3.2</h1>
<?php if ( empty($archives)) : ?>
        <p>No archives found check your configurations</p>
<?php elseif ($ok > 1) : ?>
        <ul class="archives">
<?php foreach ($archives as $a) : ?>
<?php if ($a->db_exists()) : ?>
            <li class="enabled<?= $a->id == $aid ? ' current' : '' ?>">
                <a href="./?aid=<?= $a->id ?>" target="_top"><?= $a->name ?></a>
            </li>
<?php else: ?>
                <li class="disabled">
                    <a title="<?= $a->db_error() ?>"><?= $a->name ?></a>
                </li>
<?php endif ?>
<?php endforeach ?>
        </ul>
<?php endif ?>
    </body>
</html>

