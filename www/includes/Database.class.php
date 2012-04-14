<?php defined('ROOT') ? : die('Access denied to '. __FILE__);

require_once(ROOT.'/includes/Path.class.php');
require_once(ROOT.'/includes/Folder.class.php');
require_once(ROOT.'/includes/File.class.php');
require_once(ROOT.'/includes/Version.class.php');

class Database
{
    private $path;
    private $repository;
    private $db;

    public function __construct( $path, $repository )
    {
        $this->path = $path;
        $this->repository = $repository;
        try
        {
            $this->db = new SQLite3($this->path);
        }
        catch (Exception $e)
        {
           $this->db = $e;
        }
    }

    public function __destruct()
    {
        if ($this->exists())
        {
            $this->db->close();
        }
    }

    public function exists()
    {
        return is_a($this->db, 'SQLite3');
    }

    public function error()
    {
        return is_a($this->db, 'Exception') ? $this->db->getMessage() : null;
    }

    public function get_folder($fid)
    {
        $qry = sprintf("SELECT folders.id, parent, name, paths.path FROM folders JOIN paths ON (paths.id = folders.path) WHERE folders.id = %d", $fid);
        return $this->get_object($qry, 'Folder');
    }

    public function get_folders($fid)
    {
        $qry = sprintf("SELECT folders.id, parent, name, paths.path FROM folders JOIN paths ON (paths.id = folders.path) WHERE parent = %d ORDER BY lower(name)", $fid);
        return $this->get_objects($qry, 'Folder');
    }

    public function get_path($pid)
    {
        $qry = sprintf("SELECT id, folder as parent, path FROM paths WHERE id = %d;", $pid);
        return $this->get_objects($qry, 'Path');
    }

    public function get_files($fid)
    {
        $qry = sprintf("SELECT id, folder as parent, path FROM paths WHERE NOT SUBSTR(path, -1, 1) == '/' AND folder = %d;", $fid);
        return $this->get_objects($qry, 'File');
    }

    public function get_version($vid)
    {
        $qry = sprintf("SELECT versions.id, path, created, created_i, deleted_i, checksum, size FROM versions LEFT JOIN repository ON(repository.id = versions.inode) WHERE id = %d;", $vid);
        return $this->get_object($qry, 'Path');
    }

    public function get_versions($pid)
    {
        $qry = sprintf("SELECT versions.id, path, created, created_i, deleted_i, checksum, size FROM versions LEFT JOIN repository ON(repository.id = versions.inode) WHERE path = %d;", $pid);
        return $this->get_object($qry, 'Path');
    }

    private function get_object($qry, $class=null)
    {
        $objects = $this->get_objects($qry, $class);
        return empty($objects) ? null : array_shift($objects);
    }

    private function get_objects($qry, $class=null)
    {
        $objects = Array();
        $results = $this->query($qry);
        while($row = $results->fetchArray())
        {
            $objects[] = new $class($this, $row);
        }
        return $objects;
    }
    
    private function query($qry)
    {
        @$result = $this->db->query($qry);
        if ($result === false)
        {
            die("DB Error: " . $this->db->lastErrorMsg() . "<br />" . $qry);
        }
        return $result;
    }
}
