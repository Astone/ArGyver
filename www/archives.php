<?php define('ROOT', dirname(__FILE__));

require_once('includes/all.php');

$aid = get('aid');
$fid = get('fid');
$id  = get('id');

$archive = get_archive($aid);
$archives = get_archives();

include('templates/archives.php');

