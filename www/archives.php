<?php define('ROOT', dirname(__FILE__));

require_once('includes/all.php');

$archives = get_archives(); 

include('templates/archives.php');

