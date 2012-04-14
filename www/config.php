<?php defined('ROOT') ? : die('Access denied');

# Specify the path that stores the ArGyver config files.
define('CONFIG_PATH', ROOT.'/../config');
define('CONFIG_PATTERN', '*.cfg');

ini_set('display_errors', 1); 
ini_set('log_errors', 1); 
ini_set('error_log', ROOT . '/error.log'); 
error_reporting(E_ALL);

?>
