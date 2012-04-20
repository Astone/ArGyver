<?php define('ROOT', dirname(__FILE__));

require_once('includes/all.php');

$aid      = get('aid');
$fid      = get('fid');
$pid      = get('pid');

if ($fid || $pid)
{
    $archive  = get_archive($aid);
    $path     = $pid ? $archive->get_file($pid) : $archive->get_folder($fid);
    $versions = $pid ? $path->get_versions() : $path->get_iterations();
    include('templates/versions.php');
}
