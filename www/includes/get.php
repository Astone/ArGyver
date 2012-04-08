<?php defined('security_check') ? : die('Access denied');

function get($var)
{
    if (key_exists($var, $_GET))
    {
        return $_GET[$var];
    }
    else
    {
        return null;
    }
}

?>

