<?php defined('ROOT') ? : die('Access denied to '. __FILE__);

require_once(ROOT.'/includes/DbObject.class.php');

class Version extends DbObject
{
    public function get_size()
    {
        $size = $this->get('size');
        $log = min(floor(log($size, pow(2,10))), 5);
        $txt = Array('B', 'KB', 'MB', 'GB', 'TB', 'PB');
        return sprintf("%.2f %s", $size / pow(2, 10*$log) , $txt[$log]);
    }
    
    public function is_open()
    {
        return $this->get('deleted_i') === null;
    }
}
