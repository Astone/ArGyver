<?php defined('ROOT') ? : die('Access denied to '. __FILE__);

class Version
{
    private $db;
    public $id;
    public $created;
    public $deleted;

    public function __construct($db, $id, $created, $deleted)
    {
        $this->db = $db;
        $this->id = $id;
        $this->created = $created;
        $this->deleted = $deleted;
    }

}
