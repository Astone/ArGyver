<?php defined('ROOT') ? : die('Access denied to '. __FILE__);

class Folder
{
    private $db;
    public $id;
    public $parent;
    public $name;
    private $path;
    private $versions;

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

    public function get_path()
    {
        if (empty($this->path))
        {
            $path = '';
            foreach($this->get_parents() as $p)
            {
                $path .= $p->name . '/';
            }
            $path .= $this->name . '/';
            $this->path = $this->db->get_path($path);
        }
        return $this->path;
    }

    public function get_version($vid=null)
    {
        return $this->get_path()->get_version($vid);
    }

    public function get_versions()
    {
        if (empty($this->versions))
        {
            $this->versions = $this->get_path()->get_versions();
        }
        return $this->versions;
    }

    public function is_open()
    {
        return $this->get_path()->is_open();
    }
}
