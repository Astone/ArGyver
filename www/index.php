<?php define('ROOT', dirname(__FILE__));

require_once(ROOT.'/includes/all.php');

$aid = get('aid', '?aid=1', '?aid='); # Archive ID
$fid = get('fid', '', '&fid='); # Folder ID
$id  = get( 'id', '', '&id='); # Selected Item ID

$flink = get('fid', '', '#f'); # Folder ID
$ilink = get( 'id', '', '#i'); # Selected Item ID

include('templates/index.php');

