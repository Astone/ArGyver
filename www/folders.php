<?php define('ROOT', dirname(__FILE__));

require_once('includes/all.php');

$aid      = get('aid');
$fid      = get('fid', 0);

if ( ! empty($aid))
{
    $archive  = get_archive($aid);
    if (empty($archive) || !$archive->exists()) exit();

    $folder   = $archive->get_folder($fid);
    $parent   = $folder->get_parent();
    $parents  = $folder->get_parents();
    $siblings = empty($fid) ? $folder->get_folders() : $parent->get_folders();
    $children = $folder->get_folders();

    include('templates/folders.php');
}
