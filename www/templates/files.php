<?php defined('ROOT') ? : die('Access denied to '. __FILE__) ?>
<html>
    <head>
        <title>ArGyvers Files</title>
        <link rel="stylesheet" type="text/css" href="./css/main.css" />
        <link rel="stylesheet" type="text/css" href="./css/files.css" />
    <head>
    <body>
        <h1><?= $folder->name ?></h1>
<?php if (! empty($children) || ! empty($files)) : ?>
        <table width="100%" cellspacing="0" border="0">
            <thead>
                <tr>
                    <th>File</th>
                    <th>First version</th>
                    <th>Last version</th>
                    <th>Versions</th>
                </tr>
            </thead>
            <tbody>
<?php foreach($children as $c) : ?>
                <tr class="folder">
                    <td>[<a href="./?aid=<?=$aid?>&fid=<?=$c->id?>" target="_top"><?=$c->name?></a>]</td>
                    <td></td>
                    <td></td>
                    <td></td>
                </tr>
<?php endforeach ?>
<?php foreach($files as $p) : ?>
                <tr class="file<?php echo $p->id == $pid ? " current" : "" ?>">
                    <td>
                        <?php echo $p->id == $pid ? "<a name=\"p$pid\" />" : "" ?>
                        <a href="./?aid=<?=$aid?>&fid=<?=$fid?>&pid=<?=$p->id?>" target="_top"><?=$p->name?></a>
                    </td>
                    <td><?=date("d-m-Y H:i:s", $p->get_first_version()->created)?></td>
                    <td><?=date("d-m-Y H:i:s", $p->get_last_version()->created)?></td>
                    <td><?=sizeof($p->get_versions())?></td>
                </tr>
<?php endforeach ?>
            </tbody>
        </table>
<?php else : ?>
        <p>This folder is empty.</p>
<?php endif ?>
    </body>
</html>

