<?php defined('ROOT') ? : die('Access denied');

function get($var, $default=null, $prefix='')
{
    if (key_exists($var, $_GET) && ! empty($_GET[$var]))
    {
        return $prefix.$_GET[$var];
    }
    else
    {
        return $default;
    }
}

