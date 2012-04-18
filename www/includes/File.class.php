<?php defined('ROOT') ? : die('Access denied to '. __FILE__);

require_once(ROOT.'/includes/Item.class.php');

class File extends Item
{
    public function download($repository, $vid=null)
    {
        $file_path = $this->get_abs_path($repository, $vid);

        if (file_exists($file_path)) {
            die($this->get_size());
            header('Content-Description: File Transfer');
            header('Content-Type: application/octet-stream');
            header('Content-Disposition: attachment; filename='.$this->name);
            header('Content-Transfer-Encoding: binary');
            header('Expires: 0');
            header('Cache-Control: must-revalidate');
            header('Pragma: public');
            header('Content-Length: ' . $this->get_size(false));
            ob_clean();
            flush();
            readfile($file_path);
            exit();
        }
        else
        {
            die('File not found.');
        }
    }
}
