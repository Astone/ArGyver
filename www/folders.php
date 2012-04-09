<?php define('ROOT', dirname(__FILE__));

require_once('includes/all.php');

$aid      = get('aid');
$fid      = get('fid', 0);

$archive  = get_archive($aid);

if ( ! empty($archive))
{
    $folder   = $archive->get_folder($fid);
    $parents  = $folder->get_parents();
    $siblings = $folder->get_siblings();
    $children = $folder->get_children();
    include('templates/folders.php');
}
