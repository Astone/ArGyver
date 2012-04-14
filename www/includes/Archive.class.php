<?php defined('ROOT') ? : die('Access denied to '. __FILE__);

require_once(ROOT.'/includes/Database.class.php');
require_once(ROOT.'/includes/Folder.class.php');

class Archive
{
    public $id;
    public $name;

    private $path;
    private $repository;
    private $database;

    private $db;

    private $root_pattern = "/^root\s*:\s*(\.*)/";
    private $repo_pattern = "/^repository\s*:\s*(\.*)/";
    private $db_pattern   = "/^database\s*:\s*(\.*)/";

    private $default_root = ROOT;
    private $default_repo = ".data/";
    private $default_db   = ".data.sqlite";

    public function __construct($id, $cfg_name, $cfg_path)
    {
        $this->id = $id;
        $this->name = $cfg_name;
        $this->path = $cfg_path;
    }

    private function read_config()
    {
        $file = file_get_contents($this->path);
        $lines = explode("\n", $file);
        $root_matches = preg_grep($this->root_pattern, $lines);
        $repo_matches = preg_grep($this->repo_pattern, $lines);
        $db_matches   = preg_grep($this->db_pattern,   $lines);
        $root = empty($root_matches) ? $this->default_root : trim(array_pop(explode(':', array_pop($root_matches))));
        $repo = empty($repo_matches) ? $this->default_repo : trim(array_pop(explode(':', array_pop($repo_matches))));
        $db   = empty($db_matches)   ? $this->default_db   : trim(array_pop(explode(':', array_pop($db_matches  ))));
        $this->repository = rtrim($root, '/') . '/' . $repo;
        $this->database   = rtrim($root, '/') . '/' . $db;
        $this->db = new Database($this->database, $this->repository);
    }

    private function get_db()
    {
        if ($this->db == null)
        {
            $this->read_config();
        }
        return $this->db;
    }

    public function db_exists()
    {
        $db = $this->get_db();
        return $db->exists();
    }

    public function db_error()
    {
        $db = $this->get_db();
        return $db->error();
    }

    public function get_folder($fid)
    {
        $db = $this->get_db();
        if ($fid === 0) return new Folder($db, Array('id' => 0));
        return $db->get_folder($fid);
    }

    public function get_folders($fid)
    {
        $db = $this->get_db();
        return $db->get_folders($fid);
    }

    public function get_path($pid)
    {
        $db = $this->get_db();
        return $db->get_path($pid);
    }

    public function get_paths($fid)
    {
        $db = $this->get_db();
        return $db->get_paths($fid);
    }

    public function get_version($vid)
    {
        $db = $this->get_db();
        return $db->get_version($vid);
    }

    public function get_versions($pid)
    {
        $db = $this->get_db();
        return $db->get_versions($pid);
    }

}

