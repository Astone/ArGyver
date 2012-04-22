<?php defined('ROOT') ? : die('Access denied');

setlocale(LC_ALL, 'nl_NL');

# Specify the path that stores the ArGyver config files.
define('CONFIG_PATH', ROOT.'/../config');
define('CONFIG_PATTERN', '*.cfg');

define('LONG_DATE_FORMAT', 'D j F Y' ); # d Month yyyy
define('DATE_FORMAT', 'd-m-Y' ); # dd-mm-yyyy
define('TIME_FORMAT', 'H:i' );   # hh:mm

define('ICON_PATH', "./img/ext/%s.png");

?>
