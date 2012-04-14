<?php defined('ROOT') ? : die('Access denied to '. __FILE__);

class File
{
    private $db;
    public $id;
    public $name;
    public $version;
    private $versions;
    private $open;
    private $size;

    public function __construct($db, $id, $path, $vid=None)
    {
        $this->db = $db;
        $this->id = $id;
        $this->name = basename($path);
        if (!empty($vid))
        {
            $this->version = $db->get_version($vid);
        }
    }

    public function get_version()
    {
        if (empty($this->versions))
        {
            $this->versions = $this->db->get_versions($this->id);
        }
        return $this->versions;
    }

    public function get_versions()
    {
        if (empty($this->version))
        {
            $this->version = $this->get_last_version();
        }
        return $this->version;
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

    public function get_size()
    {
        $size = $this->size;
        $log = min(floor(log($size, pow(2,10))), 5);
        $txt = Array('B', 'KB', 'MB', 'GB', 'TB', 'PB');
        return sprintf("%.2f %s", $size / pow(2, 10*$log) , $txt[$log]);
    }
}
