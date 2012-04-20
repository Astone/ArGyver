<?php define('ROOT', dirname(__FILE__));

require_once('includes/all.php');

$aid      = get('aid');
$pid      = get('pid');
$fid      = get('fid');
$vid      = get('vid');
$iid      = get('iid');

$archive  = get_archive($aid);
if ($fid) $archive->get_folder($fid)->download($archive->get_repository(), $iid);
if ($pid) $archive->get_file($pid)->download($archive->get_repository(), $vid);

