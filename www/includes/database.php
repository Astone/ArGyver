<?php defined('ROOT') ? : die('Access denied to '. __FILE__);

class Database
{
    private $path;
    private $repository;
    private $db;

    public function __construct( $path, $repository )
    {
        $this->path = $path;
        $this->repository = $repository;
        if (file_exists($this->path))
        {
            $this->db = new SQLite3($this->path);
        }
    }

    public function __destruct()
    {
        if ( ! empty($this->db))
        {
            $this->db->close();
        }
    }
    
    public function get_tree($fid)
    {
    }
}
