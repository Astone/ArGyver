<?php define('ROOT', dirname(__FILE__));

require_once('includes/all.php');

$aid      = get('aid');
$fid      = get('fid');
$pid      = get('pid');

$archive  = get_archive($aid);

if ( ! empty($archive))
{
    $folder   = $archive->get_folder($fid);
    if ( ! empty($folder))
    {
        $children = $folder->get_children();
        $files    = $folder->get_files();
        include('templates/files.php');
    }
}
