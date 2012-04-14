<?php defined('ROOT') ? : die('Access denied');

# Cast the value to an int if it is a string storing an int.
function get($var, $default=null, $prefix='')
{
    if (key_exists($var, $_GET) && $_GET[$var] !== '')
    {
        $val = $_GET[$var];
        if (empty($prefix) && (string) (int) $val === $val)
        {
            return (int) $val;
        }
        else
        {
            return $prefix.$val;
        }
    }
    else
    {
        return $default;
    }
}

