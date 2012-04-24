<?php define('ROOT', dirname(__FILE__));

require_once('includes/all.php');

$aid      = get('aid');
$id       = get('id');
$vid      = get('vid');

$archive  = get_archive($aid);
$item     = $archive->get_item($id);

header('Content-Type: image/png');
ob_clean();
flush();
readfile($item->get_thumbnail_path($vid));
exit();

