<?php define('ROOT', dirname(__FILE__));

require_once('includes/all.php');

$aid      = get('aid');
$pid      = get('pid');
$vid      = get('vid');

$archive  = get_archive($aid);

$file = $archive->get_file($pid);
$file_path = $archive->get_abs_path($pid);

if (file_exists($file_path)) {
    header('Content-Description: File Transfer');
    header('Content-Type: application/octet-stream');
    header('Content-Disposition: attachment; filename='.$file->name);
    header('Content-Transfer-Encoding: binary');
    header('Expires: 0');
    header('Cache-Control: must-revalidate');
    header('Pragma: public');
    header('Content-Length: ' . $file->get_size(false));
    ob_clean();
    flush();
    readfile($file_path);
    exit;
}
?>
