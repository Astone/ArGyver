<?php defined('ROOT') ? : die('Access denied to '. __FILE__);

require_once(ROOT.'/includes/DbObject.class.php');

class Path extends DbObject
{
    protected $version;

    public function __construct($db, $data=Array())
    {
        DbObject::__construct($db, $data);
        $this->name = basename($this->get('path'));
    }
    
    public function get_parent()
    {
        return $this->get('parent', 'get_folder');
    }

    public function get_parents()
    {
        $pointer = $this->get_parent();
        $parents = Array();
        while($pointer && $pointer->id > 0)
        {
            $parents[] = $pointer;
            $pointer = $pointer->get_parent();
        }
        return array_reverse($parents);
    }

    public function get_version($vid=null)
    {
        if (empty($this->version) || ! empty($vid))
        {
            $versions = $this->get_versions();
            if (empty($vid))
            {
                $this->version = array_pop($versions);
            }
            else
            {
                $this->version = $versions[$vid];
            }
        }
        return $this->version;
    }

    public function get_versions()
    {
        return $this->get('versions', 'get_versions', 'pid');
    }
    
    public function is_open()
    {
        if ($this->id == 0) return true;
        return $this->get_version()->is_open();
    }
}

