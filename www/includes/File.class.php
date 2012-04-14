<?php defined('ROOT') ? : die('Access denied to '. __FILE__);

require_once(ROOT.'/includes/Path.class.php');

class File extends Path
{
    public function get_size($pretty=true)
    {
        return $this->get_version()->get_size($pretty);
    }
}
