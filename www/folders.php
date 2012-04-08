<?php define('ROOT', dirname(__FILE__));

require_once('includes/all.php');

function get_tree($cid, $fid)
{
    $cfgs = get_configs();
    $html = "";
    foreach($cfgs as $cfg)
    {
        $name = "X";
        $html .= "<li>$name<ul></ul></li>";
    }
    return "<ul>$html</ul>";
}
 
include('templates/folders.php');

