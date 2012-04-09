<?php defined('ROOT') ? : die('Access denied to '. __FILE__);

class Folder
{
    private $db;
    public $id;
    public $parent;
    public $name;
    
    public function __construct($db, $id, $name, $parent=0)
    {
        $this->db = $db;
        $this->id = $id;
        $this->name = $name;
        $this->parent = $parent;
    }   

    public function get_parent()
    {
        return $this->db->get_folder($this->parent);
    }
    
    public function get_parents()
    {
        $parents = Array();
        $parent = $this;
        while($parent->parent > 0)
        {
            $parent = $parent->get_parent();
            $parents[] = $parent;
        }
        return array_reverse($parents);
    }
    
    public function get_siblings()
    {
        return $this->db->get_children($this->parent);
    }
    
    public function get_children()
    {
        return $this->db->get_children($this->id);
    }
    
    public function get_files()
    {
        return $this->db->get_files($this->id);
    }
    
}
