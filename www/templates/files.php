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
                    <th>Size</th>
                    <th>First version</th>
                    <th>Last version</th>
                    <th>Versions</th>
                </tr>
            </thead>
            <tbody>
<?php foreach($children as $c) : ?>
                <tr>
                    <td>[<a href="./?aid=<?=$aid?>&fid=<?=$c->id?>" target="_top"><?=$c->name?></a>]</td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                </tr>
<?php endforeach ?>
<?php foreach($files as $f) : ?>
                <tr>
                    <td><a href="./?aid=<?=$aid?>&fid=<?=$fid?>&pid=<?=$f->id?>" target="_top"><?=$f->name?></a></td>
                    <td><?=$f->get_size()?></td>
                    <td><?=$f->get_first_version()?></td>
                    <td><?=$f->get_last_version()?></td>
                    <td><?=sizeof($f->get_versions())?></td>
                </tr>
<?php endforeach ?>
            </tbody>
        </table>
<?php else : ?>
        <p>This folder is empty.</p>
<?php endif ?>
    </body>
</html>

