<?php defined('ROOT') ? : die('Access denied to '. __FILE__) ?>
<html>
    <head>
        <title>ArGyvers Files</title>
        <link rel="stylesheet" type="text/css" href="./css/main.css" />
        <link rel="stylesheet" type="text/css" href="./css/files.css" />
        <script src="./js/files.js" language="JavaScript"></script>
    <head>
    <body>
        <h1><?php echo $folder->name ? $folder->name : $archive->name ?></h1>
<?php if (! empty($folders) || ! empty($files)) : ?>
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
<?php foreach($folders as $f) : ?>
                <tr class="folder <?php echo $f->is_open() ? "open" : "closed" ?>">
                    <td>
                    <?php echo $f->get_path_id() == $pid ? "<a name=\"p$pid\" />" : "" ?>
                    <?php $icon=get_icon('dir') ?>
                    <?php echo $icon ? "<img src=\"$icon\" alt=\"$f->name\" width=\"16\" height=\"16\" />" : '' ?>
                    <a href="./?aid=<?=$aid?>&fid=<?=$f->id?>" target="_top" title="open folder"><?=$f ->name?></a>
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
                    <td class="versions"><?=sizeof($f->get_iterations())?></td>
                </tr>
<?php endforeach ?>
<?php foreach($files as $p) : ?>
                <tr class="file<?php echo $p->id == $pid ? " current" : "" ?> <?php echo $p->is_open() ? "open" : "closed" ?>">
                    <td class="name">
                        <?php echo $p->id == $pid ? "<a name=\"p$pid\" />" : "" ?>
                        <a href="./download.php?aid=<?=$aid?>&pid=<?=$p->id?>" target="_blank" title="download">
                        <?php $icon=get_icon($p->name) ?>
                        <?php echo $icon ? "<img src=\"$icon\" alt=\"$p->name\" width=\"16\" height=\"16\" />" : '<b>[&darr;]</b>' ?>
                        </a>
                        <a href="./?aid=<?=$aid?>&fid=<?=$fid?>&pid=<?=$p->id?>" target="_top" title="show versions"><?=$p->name?></a>
                    </td>
                    <td class="date"><?=date("d-m-Y", $p->get_version()->get_mtime())?></td>
                    <td class="time"><?=date("H:i:s", $p->get_version()->get_mtime())?></td>
                    <td class="size"><?=$p->get_size()?></td>
                    <td class="versions"><?=sizeof($p->get_versions())?></td>
                </tr>
<?php endforeach ?>
            </tbody>
        </table>
<?php else : ?>
        <p>This folder is empty.</p>
<?php endif ?>
    </body>
</html>

