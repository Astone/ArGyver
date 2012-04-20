<?php defined('ROOT') ? : die('Access denied to '. __FILE__);

require_once(ROOT.'/includes/DbObject.class.php');

class Item extends DbObject
{
    protected $version;

    public function __construct($db, $data=Array())
    {
        DbObject::__construct($db, $data);
        $this->name = $this->get('name');
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
        if ($vid || empty($this->version))
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
        return $this->get('versions', 'get_versions', 'id');
    }

    public function get_size($pretty=true)
    {
        return $this->get_version()->get_size($pretty);
    }

    public function get_abs_path($repository, $vid=null)
    {
        return $this->get_version($vid)->get_abs_path($repository);
    }

    public function exists()
    {
        if ($this->id == 0) return true;
        return $this->get_version()->exists();
    }

    public function is_folder()
    {
        if (is_a($this, 'Folder')) return True;
        if ($this->get_version()->get_inode()) return False;
        return True;
    }
}

