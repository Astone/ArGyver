<?php define('ROOT', dirname(__FILE__));

require_once('includes/all.php');

$aid      = get('aid');
$fid      = get('fid');
$pid      = get('pid');
$vid      = get('pid');

echo '<pre>';

$archive  = get_archive($aid);
#print_r($archive);

$folder = $archive->get_folder($fid);
#print_r($folder);

$parent = $folder->get_parent();
#print_r($parent);

$parents = $folder->get_parents();
#print_r($parents);

$folders = $folder->get_folders();
#print_r($folders);

$files = $folder->get_files();
#print_r($files);

$file = $files[0];
print_r($file);

