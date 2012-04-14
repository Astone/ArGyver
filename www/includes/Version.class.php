<?php defined('ROOT') ? : die('Access denied to '. __FILE__);

require_once(ROOT.'/includes/DbObject.class.php');

class Version extends DbObject
{
    public function get_size($pretty=True)
    {
        $size = $this->get('size');

        if ( !$pretty ) return $size;
        
        $log = min(floor(log($size, pow(2,10))), 5);
        $txt = Array('B', 'KB', 'MB', 'GB', 'TB', 'PB');
        return sprintf("%.2f %s", $size / pow(2, 10*$log) , $txt[$log]);
    }
    
    public function get_created()
    {
        return $this->get('created');
    }

    public function is_open()
    {
        return $this->get('deleted_i') === null;
    }
    
    public function get_abs_path($root)
    {
        $checksum = $this->get('checksum');
        return $root . '/' . substr($checksum, 0, 2) . '/' . $checksum;
    }
}
