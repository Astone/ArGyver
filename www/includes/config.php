<?php defined('ROOT') ? : die('Access denied to '. __FILE__);

require_once(ROOT.'/config.php');

class Config
{
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

    public function __construct($cfg_path)
    {
        $this->path = $cfg_path;
    }
    
    public function get_db()
    {
        if ($this->db == null)
        {
            $this->read_config();
        }
        return $this->db;
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
        $this->repository = $root . '/' . $repo;
        $this->database   = $root . '/' . $db;
        $this->db = new Database($this->database, $this->repository);
    }
}

function get_configs()
{
    $configs = Array();
    foreach(glob_recursive(CONFIG_PATH . '/' . CONFIG_PATTERN) as $cfg_path)
    {
        $cfg_info = pathinfo($cfg_path);
        $cfg_name = $cfg_info['filename'];
        $configs[$cfg_name] = new Config($cfg_path);
    }
    return $configs;
}

