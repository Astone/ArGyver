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

    public function get_folder($fid, $class='Folder')
    {
        if ($fid === 0) return new Folder($this, Array('id'=>0));
        $qry = sprintf("SELECT folders.id, parent, name, paths.path, folders.id as fid, paths.id as pid FROM folders JOIN paths ON (paths.id = folders.path) WHERE folders.id = %d", $fid);
        return $this->get_object($qry, $class);
    }

    public function get_folders($fid, $class='Folder')
    {
        $qry = sprintf("SELECT folders.id, parent, name, paths.path, folders.id as fid, paths.id as pid FROM folders JOIN paths ON (paths.id = folders.path) WHERE parent = %d ORDER BY lower(name)", $fid);
        return $this->get_objects($qry, $class);
    }

    public function get_path($pid, $class='Path')
    {
        $qry = sprintf("SELECT id, folder as parent, path, id as pid FROM paths WHERE id = %d;", $pid);
        return $this->get_object($qry, $class);
    }

    public function get_files($fid, $class='File')
    {
        $qry = sprintf("SELECT id, folder as parent, path, id as pid FROM paths WHERE NOT SUBSTR(path, -1, 1) == '/' AND folder = %d;", $fid);
        return $this->get_objects($qry, $class);
    }

    public function get_version($vid, $class='Version')
    {
        $qry = sprintf("SELECT versions.id, path, created, created_i, deleted_i, checksum, size FROM versions LEFT JOIN repository ON(repository.id = versions.inode) WHERE id = %d;", $vid);
        return $this->get_object($qry, $class);
    }

    public function get_versions($pid, $class='Version')
    {
        $qry = sprintf("SELECT versions.id, path, created, created_i, deleted_i, checksum, size FROM versions LEFT JOIN repository ON(repository.id = versions.inode) WHERE path = %d ORDER BY created_i;", $pid);
        return $this->get_objects($qry, $class);
    }

    public function get_iterations($pid, $class='Version')
    {
        $qry = sprintf("
            SELECT
                i.id,
                i.id AS created_i,
                i.id+1 AS deleted_i,
                i.start AS created
            FROM versions AS v
                JOIN paths AS p ON (p.id = v.path AND p.id = %d)
                JOIN iterations AS i ON (i.id >= v.created_i AND (i.id < v.deleted_i OR v.deleted_i IS NULL))
            ORDER BY i.id;", $pid);
        return $this->get_objects($qry, $class);
    }

    public function get_iteration_timestamp($iid)
    {
        $qry = sprintf("SELECT start FROM iterations WHERE id = %d;", $iid);
        return $this->get_value($qry);
    }

    private function get_value($qry, $key = null)
    {
        $object = $this->get_object($qry);
        return empty($object) ? null : empty($key) ? array_shift($object) : $object[$key];
    }

    private function get_values($qry, $key = null)
    {
        $objects = $this->get_objects($qry);
        $values = Array();
        foreach ($objects as $o)
        {
            $values[] = empty($key) ? array_shift($o) : $o[$key];
        }
        return $values;
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
            if (array_key_exists('id', $row))
            {
                $objects[$row['id']] = empty($class) ? $row : new $class($this, $row);
            }
            else
            {
                $objects[] = empty($class) ? $row : new $class($this, $row);
            }
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
