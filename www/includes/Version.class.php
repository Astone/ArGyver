<?php defined('ROOT') ? : die('Access denied to '. __FILE__);

require_once(ROOT.'/includes/DbObject.class.php');

class Version extends DbObject
{
    public function get_size($pretty=True)
    {
        $size = $this->get('size');
        return $pretty ? pretty_file_size($size) : $size;
    }
    
    public function get_inode()
    {
        return $this->get('inode');
    }
    
    public function get_checksum()
    {
        return $this->get('checksum');
    }
    
    public function get_mtime()
    {
        return $this->get('time');
    }

    public function get_deleted()
    {
        return $this->get('deleted', 'get_iteration_timestamp');
    }

    public function get_created()
    {
        return $this->get('created', 'get_iteration_timestamp');
    }

    public function exists()
    {
        return $this->get_deleted() === null;
    }
    
    public function get_abs_path($root)
    {
        $checksum = $this->get_checksum();
        return $root . '/' . substr($checksum, 0, 2) . '/' . $checksum;
    }
}
