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

    public function get_iterations()
    {
        return $this->get('iterations', 'get_iterations', 'pid');
    }

    public function get_path_id()
    {
        return $this->get('pid');
    }

    public function get_size($pretty=true, $calculate = false)
    {    
        $aid = get('aid');

        @ $size = $_SESSION['FOLDER_SIZES'][$aid][$this->id];

        if ($calculate) $size = $this->calculate_size();

        if ($size === null) $size = 'unknown';
        
        if (substr($size, 0, 1) == '~') $size = 'canceled';
        
        $size = (! $pretty && ! is_numeric($size)) ? null : $size;

        return ($pretty && is_numeric($size)) ? pretty_file_size($size) : $size;
    }
    
    public function calculate_size($max_time=null, $done = null)
    {
        if ($max_time < 0) return '~';

        $start = time();
        
        $aid = get('aid');

        @ $size = $_SESSION['FOLDER_SIZES'][$aid][$this->id];

        if (is_numeric($size)) return $size;

        $_SESSION['FOLDER_SIZES'][$aid][$this->id] = 'calculating';

        if ( ! $this->is_open() )
        {
            $_SESSION['FOLDER_SIZES'][$aid][$this->id] = 'deleted';
            return 0;
        }
        
        $size = 0;

        $folders = $this->get_folders();
        $this->reset();
        foreach ($folders as $f)
        {
            @ $sub_size = $_SESSION['FOLDER_SIZES'][$aid][$f->id];
            if (! is_numeric($sub_size)) $_SESSION['FOLDER_SIZES'][$aid][$f->id] = 'pending';
        }

        foreach ($folders as $f)
        {
            $time_left = $max_time===null ? null : $max_time - (time() - $start);
            $sz = $f->calculate_size($time_left);
            if (substr($sz, 0, 1) == '~')
            {
                $size = '~'.($size+substr($sz, 1));
                $_SESSION['FOLDER_SIZES'][$aid][$this->id] = $size;
                return $size; 
            }
            $size += $sz;
        }

        foreach ($this->get_files() as $f)
        {
            $size += $f->get_size(false);
        }

        $_SESSION['FOLDER_SIZES'][$aid][$this->id] = $size;

        return $size;
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
        $folders = $this->get_folders();
        $this->reset();
        foreach($folders as $f)
        {
            $f->_add_to_zip($zip, $repository, $root.'/'.$f->name);
        }        

        foreach($this->get_files() as $f)
        {
            $zip->add_file_from_path($root.'/'.$f->name, $f->get_abs_path($repository));
        }        
    }
}
