<?php define('ROOT', dirname(__FILE__));

require_once('includes/all.php');

$aid      = get('aid');
$id       = get('id');

if ($id)
{
    $archive  = get_archive($aid);
    $item     = $archive->get_item($id);
    $versions = $item->get_versions();
    include('templates/versions.php');
}
