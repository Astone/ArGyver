<?php defined('ROOT') ? : die('Access denied to '. __FILE__);

require_once(ROOT.'/includes/DbObject.class.php');

class Path extends DbObject
{
    public function get_parent()
    {
        return $this->get('parent', 'get_folder');
    }

    public function get_parents()
    {
        $pointer = $this;
        $parents = Array();
        while($pointer = $pointer->get_parent())
        {
            $parents[] = $pointer;
        }
        return array_reverse($parents);
    }
}

