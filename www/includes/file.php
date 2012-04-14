<?php defined('ROOT') ? : die('Access denied to '. __FILE__);

class File
{
    private $db;
    public $id;
    public $name;
    public $version;
    private $versions;

    public function __construct($db, $id, $path, $vid=null)
    {
        $this->db = $db;
        $this->id = $id;
        $this->name = basename($path);
        if (!empty($vid))
        {
            $this->version = $this->get_version($vid);
        }
    }

    public function get_version($vid=null)
    {
        if (empty($this->version))
        {
            $this->version = $this->get_last_version();
        }
        return $this->version;
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
        return $this->get_version()->is_open();
    }

    public function get_size()
    {
        return $this->get_version()->get_size();
    }
}
