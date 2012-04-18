<?php defined('ROOT') ? : die('Access denied to '. __FILE__);

require_once(ROOT.'/includes/Item.class.php');
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

    public function get_item($fid, $class='Item')
    {
        $qry = sprintf("SELECT id, parent, name FROM items WHERE id = %d", $fid);
        return $this->get_object($qry, $class);
    }

    public function get_folder($fid, $class='Folder')
    {
        if ($fid === 0) return new $class($this, Array('id' => 0));
        return $this->get_item($fid, $class);
    }

    public function get_folders($fid, $class='Folder')
    {
        $qry = sprintf("SELECT DISTINCT items.id, parent, name FROM items JOIN versions ON (versions.item = items.id) WHERE parent = %d AND inode IS NULL ORDER BY lower(name)", $fid);
        return $this->get_objects($qry, $class);
    }

    public function get_files($fid, $class='File')
    {
        $qry = sprintf("SELECT DISTINCT items.id, parent, name FROM items JOIN versions ON (versions.item = items.id) WHERE parent = %d AND inode IS NOT NULL ORDER BY lower(name)", $fid);
        return $this->get_objects($qry, $class);
    }

    public function get_versions($id, $class='Version')
    {
        $qry = sprintf("SELECT id, time, created, deleted, size, inode FROM versions WHERE item = %d ORDER BY created;", $id);
        return $this->get_objects($qry, $class);
    }

    public function get_iteration_timestamp($iid)
    {
        $qry = sprintf("SELECT time FROM iterations WHERE id = %d;", $iid);
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
