<?php defined('ROOT') ? : die('Access denied to '. __FILE__);

require_once(ROOT.'/includes/DbObject.class.php');

class Item extends DbObject
{
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
        $versions = $this->get_versions();
        if (empty($versions)) return null;
        if (empty($vid)) $vid = end(array_keys($versions));
        return $versions[$vid];
    }

    public function get_versions()
    {
        return $this->get('versions', 'get_versions', 'id');
    }

    public function get_size($pretty=true, $vid=null)
    {
        return $this->get_version($vid)->get_size($pretty);
    }

    public function get_abs_path($vid=null)
    {
        return $this->get_version($vid)->get_abs_path();
    }

    public function exists($vid=null)
    {
        if ($this->id == 0) return true;
        return $this->get_version($vid)->exists();
    }

    public function is_folder($vid=null)
    {
        if (is_a($this, 'Folder')) return True;
        if ($this->get_version($vid)->get_inode()) return False;
        return True;
    }

    public function get_thumbnail_path($vid=null)
    {
        return $this->get_version($vid)->get_thumbnail_path();
    }

    public function has_thumbnail($vid=null)
    {
        return $this->get_version($vid)->has_thumbnail();
    }
}

