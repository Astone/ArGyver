<?php defined('ROOT') ? : die('Access denied to '. __FILE__) ?>
<html>
    <head>
        <title>ArGyvers Files</title>
        <link rel="stylesheet" type="text/css" href="./css/main.css" />
        <link rel="stylesheet" type="text/css" href="./css/files.css" />
        <script src="./js/files.js" language="JavaScript"></script>
    <head>
    <body>
<?php if ($parent) : ?></h1>
        <h1><a href="./?aid=<?=$aid?>&fid=<?=$parent->id?>&id=<?=$parent->id?>" title="<?=$parent->name ?>" target="_top">&laquo;</a> <?=$folder->name?></h1>
<?php else : ?></h1>
        <h1><?=$archive->name ?></h1>
<?php endif ?></h1>
<?php if (! empty($items)) : ?>
        <table width="100%" cellspacing="0" border="0">
            <thead>
                <tr>
                    <th>File</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Size</th>
                    <th>Versions</th>
                </tr>
            </thead>
            <tbody>
<?php foreach($items as $f) : ?>
                <tr class="file<?php echo $f->id == $id ? " current" : "" ?> <?php echo $f->exists() ? "open" : "closed" ?>">
                    <td class="name">
                        <?php echo $f->id == $id ? "<a name=\"i$id\" />" : "" ?>
                        <a href="./download.php?aid=<?=$aid?>&id=<?=$f->id?>" target="_blank" title="Download <?=$f->name?>">
                        <?php $icon=get_icon( is_a($f, 'Folder') ? 'dir' : $f->name) ?>
                        <?php echo $icon ? "<img src=\"$icon\" alt=\"$f->name\" width=\"16\" height=\"16\" />" : '<b>[&darr;]</b>' ?>
                        </a>
                        <a href="./?aid=<?=$aid?>&fid=<?php echo is_a($f, 'Folder') ? $f->id: $fid ?>&id=<?=$f->id?>" target="_top" title="Show versions of <?=$f->name?>"><?=$f->name?></a>
                    </td>
                    <td class="date"><?=date("d-m-Y", $f->get_version()->get_mtime())?></td>
                    <td class="time"><?=date("H:i:s", $f->get_version()->get_mtime())?></td>
                    <td class="size">
<?php if($f->get_size(false) === null) : ?>
                    <a href="./calculate_size.php?aid=<?=$aid?>&fid=<?=$f->id?>" target="_self" title="calculate size" onclick="return calculate_size('<?= str_replace('\'', '\\\'', $f->name) ?>');"><?= $f->get_size(true) ?></a>
<?php else : ?>
                    <?= $f->get_size(true) ?>
<?php endif ?>
                    </td>
                    <td class="versions"><?=sizeof($f->get_versions())?></td>
                </tr>
<?php endforeach ?>
            </tbody>
        </table>
<?php else : ?>
        <p>This folder is empty.</p>
<?php endif ?>
    </body>
</html>

