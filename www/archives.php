<?php define('ROOT', dirname(__FILE__));

require_once('includes/all.php');

$aid = get('aid');
$fid = get('fid');
$id  = get('id');

$archive = get_archive($aid);
$archives = get_archives();

$ok = 0;
foreach ($archives as $a) if ($a->exists()) $ok += 1;

include('templates/archives.php');

