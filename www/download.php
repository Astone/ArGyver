<?php define('ROOT', dirname(__FILE__));

require_once('includes/all.php');

$aid      = get('aid');
$id       = get('id');
$vid      = get('vid');

$archive  = get_archive($aid);
$item     = $archive->get_item($id);
$version  = $item->get_version($vid);

$item     = $version->get_inode() ? $archive->get_file($id) : $archive->get_folder($id);

$item->download($vid);

