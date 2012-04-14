<?php defined('ROOT') ? : die('Access denied to '. __FILE__);

require_once(ROOT.'/config.php');
require_once(ROOT.'/includes/Archive.class.php');

function get_archives()
{
    $archives = Array();
    $i = 0;
    foreach(glob_recursive(CONFIG_PATH . '/' . CONFIG_PATTERN) as $cfg_path)
    {
        $i++;
        $cfg_info = pathinfo($cfg_path);
        $cfg_name = $cfg_info['filename'];
        $archives[] = new Archive($i, $cfg_name, $cfg_path);
    }
    return $archives;
}

function get_archive($aid)
{
    $archives = get_archives();
    return $archives[$aid-1];
}

