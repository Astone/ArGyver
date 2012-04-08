<?php define('ROOT', dirname(__FILE__));

require_once('includes/all.php');

function get_tree($cid, $fid)
{
    return "(tree)";
}
 
include('templates/folders.php');

