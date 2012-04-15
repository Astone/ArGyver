<?php define('ROOT', dirname(__FILE__));

require_once(ROOT.'/includes/all.php');

if (isset($_GET['clear_session'])) unset($_SESSION);

$aid = get('aid', '?aid=1', '?aid='); # Archive ID
$fid = get('fid', '', '&fid='); # Folder ID
$pid = get('pid', '', '&pid='); # Path ID
$vid = get('vid', '', '&vid='); # Version ID

$flink = get('fid', '', '#f'); # Folder ID
$plink = get('pid', '', '#p'); # Path ID
$vlink = get('vid', '', '#v'); # Version ID

include('templates/index.php');

