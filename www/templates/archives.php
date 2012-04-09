<?php defined('ROOT') ? : die('Access denied to '. __FILE__) ?>
<html>
    <head>
        <title>ArGyvers Header</title>
        <link rel="stylesheet" type="text/css" href="./css/main.css" />
        <link rel="stylesheet" type="text/css" href="./css/archives.css" />
    <head>
    <body>
        <h1>ArGyver v3.1 alpha</h1>
<?php if ($archives) : ?>
        <ul class="archives">
<?php foreach ($archives as $archive) : ?>
<?php if ($archive->db_exists()) : ?>
            <li class="enabled<?= $archive->id == get('aid') ? current : '' ?>">
                <a href="./?aid=<?= $archive->id ?>" target="_top"><?= $archive->name ?></a>
            </li>
<?php else: ?>
                <li class="disabled">
                    <a title="<?= $archive->db_error() ?>"><?= $archive->name ?></a>
                </li>
<?php endif ?>
<?php endforeach ?>
        </ul>
<?php endif ?>
    </body>
</html>

