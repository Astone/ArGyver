<?php defined('ROOT') ? : die('Access denied');

if ($vid = get('vid'))
{
    define('MIN_V', $vid);
    define('MAX_V', $vid);
}
else
{
    if (isset($_SESSION['VERSION_LOWER_BOUND']))
    {
        define('MIN_V', $_SESSION['VERSION_LOWER_BOUND']);
    }
    else
    {
        define('MIN_V', 0);
    }
    if (isset($_SESSION['VERSION_UPPER_BOUND']))
    {
        define('MAX_V', $_SESSION['VERSION_UPPER_BOUND']);
    }
    else
    {
        define('MAX_V', PHP_INT_MAX);
    }
}

