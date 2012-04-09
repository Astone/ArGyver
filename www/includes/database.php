<?php defined('ROOT') ? : die('Access denied to '. __FILE__);

require_once('includes/folder.php');
require_once('includes/file.php');

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
        if ($id===null)
        {
            return null;
        }
        $qry = sprintf("SELECT * FROM folders WHERE id = %d", $id);

        return $this->get_folder_from_qry($qry);
    }

    public function get_children($id)
    {
        $qry = sprintf("SELECT * FROM folders WHERE parent = %d", $id);

        return $this->get_folders_from_qry($qry);
    }

    private function get_folder_from_qry($qry)
    {
        $folders = $this->get_folders_from_qry($qry);

        if ($folders)
        {
            return $folders[0];
        }
        else
        {
            return new Folder($this, 0, '', 0);
        }
    }

    private function get_folders_from_qry($qry)
    {
        $results = $this->db->query($qry);

        $folders = Array();
        
        while($folder = $results->fetchArray())
        {
            $folders[] = new Folder($this, $folder['id'], $folder['name'], $folder['parent']);
        }
        return $folders;
    }

    public function get_files($id)
    {
        if ($id===null)
        {
            return null;
        }
        $qry = sprintf("SELECT * FROM paths WHERE folder = %d", $id);

        return $this->get_files_from_qry($qry);
    }

    private function get_file_from_qry($qry)
    {
        $files = $this->get_files_from_qry($qry);

        if ($files)
        {
            return $files[0];
        }
        else
        {
            return new File($this, 0, '');
        }
    }

    private function get_files_from_qry($qry)
    {
        $results = $this->db->query($qry);

        $files = Array();
        
        while($file = $results->fetchArray())
        {
            $files[] = new File($this, $file['id'], $file['path']);
        }
        return $files;
    }
}
