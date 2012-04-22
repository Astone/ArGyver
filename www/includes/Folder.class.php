<?php defined('ROOT') ? : die('Access denied to '. __FILE__);

require_once(ROOT.'/includes/Item.class.php');

class Folder extends Item
{

    public function get_items()
    {
        return array_merge($this->get_folders(), $this->get_files());
    }

    public function get_folders()
    {
        return $this->get('folders', 'get_folders', 'id');
    }

    public function get_files()
    {
        return $this->get('files', 'get_files', 'id');
    }

    public function download($repository, $iid=null)
    {
        ini_set('display_errors', 0);

        $zip = new ZipStream($this->name.'.zip');
        $this->_add_to_zip($zip, $repository);
        $zip->finish();
    }
    
    private function _add_to_zip($zip, $repository, $root=null)
    {
        foreach($this->get_folders() as $f)
        {
            $f->_add_to_zip($zip, $repository, $root.'/'.$f->name);
        }        

        foreach($this->get_files() as $f)
        {
            $zip->add_file_from_path($root.'/'.$f->name, $f->get_abs_path($repository));
        }        
        $this->reset();
    }
}
