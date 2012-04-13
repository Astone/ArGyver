<?php defined('ROOT') ? : die('Access denied to '. __FILE__);

require_once('includes/folder.php');
require_once('includes/file.php');
require_once('includes/version.php');

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

    public function get_folder($id)
    {
        $qry = sprintf("SELECT * FROM folders WHERE id = %d", $id);
        return $this->get_folder_from_qry($qry);
    }

    public function get_children($id)
    {
        $qry = sprintf("SELECT * FROM folders WHERE parent = %d ORDER BY name", $id);
        return $this->get_folders_from_qry($qry);
    }

    private function get_folder_from_qry($qry)
    {
        $folders = $this->get_folders_from_qry($qry);

        if (empty($folders))
        {
            return new Folder($this, 0, '', 0);
        }
        return $folders[0];
    }

    private function get_folders_from_qry($qry)
    {
        $result = $this->query($qry);

        $folders = Array();

        if ($result)
        {
            while($folder = $result->fetchArray())
            {
                $folders[] = new Folder($this, $folder['id'], $folder['name'], $folder['parent']);
            }
            return $folders;
        }
    }

    public function get_path($path)
    {
        $qry = sprintf("SELECT * FROM paths WHERE path = %s;", $path);

        return $this->get_file_from_qry($qry);
    }

    public function get_files($id)
    {
        if ($id===null)
        {
            return null;
        }
        $qry = sprintf("SELECT * FROM paths WHERE folder = %d ORDER BY path", $id);

        return $this->get_files_from_qry($qry);
    }

    private function get_file_from_qry($qry)
    {
        $files = $this->get_files_from_qry($qry);

        if (empty($files))
        {
            return null;
        }
        return $files[0];
    }

    private function get_files_from_qry($qry)
    {
        $results = $this->query($qry);

        $files = Array();

        while($file = $results->fetchArray())
        {
            $files[] = new File($this, $file['id'], $file['path']);
        }
        return $files;
    }

    public function get_versions($id)
    {
        if ($id===null)
        {
            return null;
        }
        $qry = sprintf("SELECT * FROM versions WHERE path = %d ORDER BY created", $id);

        return $this->get_versions_from_qry($qry);
    }

    private function get_versions_from_qry($qry)
    {
        $results = $this->query($qry);

        $versions = Array();

        while($version = $results->fetchArray())
        {
            $versions[] = new Version($this, $version['id'], $version['created'], $version['deleted']);
        }
        return $versions;
    }

    private function query($qry)
    {
        @$result = $this->db->query($qry);
        if ($result === false)
        {
            die("DB Error: " . $this->db->lastErrorMsg());
        }
        return $result;
    }
}
