<?php define('ROOT', dirname(__FILE__));

require_once('includes/all.php');

$aid      = get('aid');
$pid      = get('pid');

if ( ! empty($pid))
{
    $archive  = get_archive($aid);
    $path     = $archive->get_path($pid);
    $versions = $path->get_versions();
    include('templates/versions.php');
}
