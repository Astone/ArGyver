<?php defined('ROOT') ? : die('Access denied to '. __FILE__);

class File
{
    private $db;
    public $id;
    public $name;
    private $versions;
    private $open;

    public function __construct($db, $id, $path)
    {
        $this->db = $db;
        $this->id = $id;
        $this->name = basename($path);
    }

    public function get_versions()
    {
        if (empty($this->versions))
        {
            $this->versions = $this->db->get_versions($this->id);
        }
        return $this->versions;
    }

    public function get_first_version()
    {
        $versions = $this->get_versions();
        if (empty($versions))
        {
            return null;
        }
        return $versions[0];
    }

    public function get_last_version()
    {
        $versions = $this->get_versions();
        if (empty($versions))
        {
            return null;
        }
        return $versions[sizeof($versions)-1];
    }

    public function is_open()
    {
        if ($this->open === null)
        {
            $this->open = false;
            $versions = $this->get_versions();
            foreach ($versions as $v)
            {
                if ($v->deleted === null)
                {
                    $this->open = true;
                }
            }
        }
        return $this->open;
    }
}
