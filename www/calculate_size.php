<?php define('ROOT', dirname(__FILE__) );

require_once(ROOT.'/includes/all.php');

$aid      = get('aid');
$fid      = get('fid');

$archive  = get_archive($aid);
$folder   = $archive->get_folder($fid);

$timeout = 10;

@ $size = $_SESSION['FOLDER_SIZES'][$aid][$fid];

$size = $folder->calculate_size($timeout);
$finished = is_numeric($size);
$size = $finished ? pretty_file_size($size) : pretty_file_size(substr($size, 1));

if ($finished) header(sprintf("Location: ./files.php?aid=%d&fid=%d&pid=%d", $aid, $folder->get_parent()->id, $folder->get_path_id()));

include(ROOT.'/templates/calculate_size.php');
