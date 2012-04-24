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
        $deleted = $this->get('deleted');
        return $deleted === null || $deleted > MAX_V;
    }

    public function busy()
    {
        return $this->get('created', 'get_iteration_finished') === null;
    }

    public function get_abs_path()
    {
        $checksum = $this->get_checksum();
        return $this->db->repository . '/' . substr($checksum, 0, 2) . '/' . $checksum;
    }

    public function get_thumbnail_path()
    {
        $checksum = $this->get_checksum();
        return $this->db->thumbnails . '/' . substr($checksum, 0, 2) . '/' . $checksum . '.png';
    }
    public function has_thumbnail()
    {
        return file_exists($this->get_thumbnail_path());
    }
}
