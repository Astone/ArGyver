<?php define('ROOT', dirname(__FILE__));

require_once('includes/all.php');

$aid      = get('aid');
$fid      = get('fid', 0);
$id       = get('id');

if ( ! empty($aid))
{
    $archive  = get_archive($aid);
    $folder   = $archive->get_folder($fid);
    $parent   = $folder->get_parent();
    $items    = $folder->get_items();
    include('templates/files.php');
}
