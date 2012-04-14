<?php defined('ROOT') ? : die('Access denied to '. __FILE__);

require_once(ROOT.'/includes/Path.class.php');

class Folder extends Path
{

    public function get_folders()
    {
        return $this->get('folders', 'get_folders', 'id');
    }

    public function get_files()
    {
        return $this->get('files', 'get_files', 'id');
    }

    public function get_versions()
    {
        return $this->get('versions', 'get_versions', 'id');
    }

}
