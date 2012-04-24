<?php defined('ROOT') ? : die('Access denied to '. __FILE__) ?>
<html>
    <head>
        <title>ArGyvers Files</title>
        <link rel="stylesheet" type="text/css" href="./css/main.css" />
        <link rel="stylesheet" type="text/css" href="./css/files.css" />
    <head>
    <body>
<?php if ($parent) : ?></h1>
        <a href="./?aid=<?=$aid?>&fid=<?=$parent->id?>&id=<?=$parent->id?>" title="<?=$parent->name ?>" target="_top">
            <h1><img src="./img/folder.png" alt="<?=$folder->name?>" /> <?=$folder->name?></h1>
        </a>
<?php else : ?></h1>
            <h1><img src="./img/archive.png" alt="<?=$archive->name?>" /> <?=$archive->name?></h1>
<?php endif ?></h1>
<?php if (! empty($items)) : ?>
        <table width="100%" cellspacing="0" border="0">
            <thead>
                <tr>
                    <th>File</th>
                    <th>Date</th>
                    <th>Time</th>
                    <th>Size</th>
                    <th colspan="2">Versions</th>
                </tr>
            </thead>
            <tbody>
<?php foreach($items as $f) : ?>
                <tr class="file<?php echo $f->id == $id ? " current" : "" ?> <?php echo $f->exists() ? "open" : "closed" ?>">
                    <td class="name">
                        <?php echo $f->id == $id ? "<a name=\"i$id\" />" : "" ?>
                        <a href="./?aid=<?=$aid?>&fid=<?php echo $f->is_folder() ? $f->id: $fid ?>&id=<?=$f->id?>" target="_top" title="Show versions of <?=$f->name?>">
                            <img src="<?= get_icon( $f->is_folder() ? 'folder' : $f->name)?>" alt="<?=$f->name?>" width="16" height="16" />
                            <?=str_replace(' ', '&nbsp', htmlentities($f->name))?>
                        </a>
                    </td>
                    <td class="date"><?=date(DATE_FORMAT, $f->get_version()->get_mtime())?></td>
                    <td class="time"><?=date(TIME_FORMAT, $f->get_version()->get_mtime())?></td>
                    <td class="size">
                    <?php echo $f->get_size(false) === null ? '<img src="./img/loader.gif" alt="ArGyver is busy"/>' : $f->get_size(true) ?>
                    </td>
                    <td class="versions"><?=sizeof($f->get_versions())?></td>
                    <td class="thumbnail"><?php if $f->has_thumbnail() ?><img src="./img/thumbnail.png" alt="<?=$f->name?>" /><?php endif ?></td>
                </tr>
<?php endforeach ?>
            </tbody>
        </table>
<?php else : ?>
        <p>This folder is empty.</p>
<?php endif ?>
    </body>
</html>

