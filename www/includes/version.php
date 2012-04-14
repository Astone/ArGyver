<?php defined('ROOT') ? : die('Access denied to '. __FILE__);

class Version
{
    private $db;
    public $id;
    public $time;
    public $size;
    public $created;
    public $deleted;

    public function __construct($db, $record)
    {
        $this->db       = $db;
        $this->id       = $record['id'];
        $this->time     = $record['created'];
        $this->size     = $record['size'];
        $this->created  = $record['created_i'];
        $this->deleted  = $record['deleted_i'];
    }

    public function get_size()
    {
        $size = $this->size;
        $log = min(floor(log($size, pow(2,10))), 5);
        $txt = Array('B', 'KB', 'MB', 'GB', 'TB', 'PB');
        return sprintf("%.2f %s", $size / pow(2, 10*$log) , $txt[$log]);
    }
    
    public function is_open()
    {
        return empty($this->deleted);
    }
}
