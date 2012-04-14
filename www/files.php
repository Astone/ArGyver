<?php define('ROOT', dirname(__FILE__));

require_once('includes/all.php');

$aid      = get('aid');
$fid      = get('fid', 0);
$pid      = get('pid');

if ( ! empty($aid))
{
    $archive  = get_archive($aid);
    $folder   = $archive->get_folder($fid);
    $folders = $folder->get_folders();
    $files   = $folder->get_files();
    include('templates/files.php');
}
