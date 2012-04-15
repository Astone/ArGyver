<?php defined('ROOT') ? : die('Access denied to '. __FILE__);

require_once(ROOT.'/includes/DbObject.class.php');

class Version extends DbObject
{
    public function get_size($pretty=True)
    {
        $size = $this->get('size');
        return $pretty ? pretty_file_size($size) : $size;
    }
    
    public function get_mtime()
    {
        return $this->get('created');
    }

    public function get_deleted()
    {
        return $this->get('deleted_i', 'get_iteration_timestamp');
    }

    public function get_created()
    {
        return $this->get('created_i', 'get_iteration_timestamp');
    }

    public function is_open()
    {
        return $this->get_deleted() === null;
    }
    
    public function get_abs_path($root)
    {
        $checksum = $this->get('checksum');
        return $root . '/' . substr($checksum, 0, 2) . '/' . $checksum;
    }
}
