<?php defined('ROOT') ? : die('Access denied to '. __FILE__);

require_once(ROOT.'/includes/Database.class.php');
require_once(ROOT.'/includes/Folder.class.php');

class Archive extends Database
{
    public $id;
    public $name;

    private $cfg_path
    private $repository;
    private $database;
    private $thumbnails;

    private $root_pattern = "/^root\s*:\s*(\.*)/";
    private $repo_pattern = "/^repository\s*:\s*(\.*)/";
    private $db_pattern   = "/^database\s*:\s*(\.*)/";
    private $thumb_pattern= "/^thumbnail\s*:\s*(\.*)/";

    private $default_root  = ROOT;
    private $default_repo  = ".data/";
    private $default_db    = ".data.sqlite";
    private $default_thumb = ".thumbs/";

    public function __construct($id, $cfg_name, $cfg_path)
    {
        $this->id = $id;
        $this->name = $cfg_name;
        $this->cfg_path = $cfg_path;
    }

    private function read_config()
    {
        $file = file_get_contents($this->cfg_path);
        $lines = explode("\n", $file);
        $root_matches  = preg_grep($this->root_pattern,  $lines);
        $repo_matches  = preg_grep($this->repo_pattern,  $lines);
        $db_matches    = preg_grep($this->db_pattern,    $lines);
        $thumb_matches = preg_grep($this->thumb_pattern, $lines);
        $root  = empty($root_matches)  ? $this->default_root  : trim(array_pop(explode(':', array_pop($root_matches ))));
        $repo  = empty($repo_matches)  ? $this->default_repo  : trim(array_pop(explode(':', array_pop($repo_matches ))));
        $db    = empty($db_matches)    ? $this->default_db    : trim(array_pop(explode(':', array_pop($db_matches   ))));
        $thumb = empty($thumb_matches) ? $this->default_thumb : trim(array_pop(explode(':', array_pop($thumb_matches))));
        $this->repository = rtrim($root, '/') . '/' . $repo;
        $this->database   = rtrim($root, '/') . '/' . $db;
        $this->thumbnails = rtrim($root, '/') . '/' . $thumb;
        $this->connect(db($this->database));
    }

    public function get_repository()
    {
        if ($this->repository == null)
        {
            $this->read_config();
        }
        return $this->repository;
    }

    public function get_thumbnails()
    {
        if ($this->thumbnails == null)
        {
            $this->read_config();
        }
        return $this->thumbnails;
    }
}

