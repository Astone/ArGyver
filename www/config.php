<?php defined('ROOT') ? : die('Access denied');

setlocale(LC_ALL, 'nl_NL');

# Specify the path that stores the ArGyver config files.
define('CONFIG_PATH', ROOT.'/../config');
define('CONFIG_PATTERN', '*.cfg');

define('LARGE_FILE_SIZE', 100 * 1024 * 1024 ); # 100 MB

define('LONG_DATE_FORMAT', 'D j M Y' ); # d Month yyyy
define('DATE_FORMAT', 'd-m-Y' ); # dd-mm-yyyy
define('TIME_FORMAT', 'H:i' );   # hh:mm

define('ICON_PATH', "./img/ext/%s.png");

?>
