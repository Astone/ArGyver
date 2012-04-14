<?php defined('ROOT') ? : die('Access denied to '. __FILE__);

class DbObject
{
    public $id = null;
    public $name = null;
    private $db = null;
    private $data = Array();
    private $objects = Array();
    
    public function __construct($db, $data=Array())
    {
        $this->db = $db;
        $this->data = $data;
        $this->id = $this->get('id');
        $this->name = get_class($this);
    }
    
    protected function get($key, $callback=null, $dbkey=null)
    {
        $dbkey = empty($dbkey) ? $key : $dbkey;

        if ( ! array_key_exists($dbkey, $this->data)) return null;

        if (empty($callback)) return $this->data[$dbkey];
        
        if (array_key_exists($dbkey, $this->data) && ! array_key_exists($key, $this->objects))
        {
            $this->objects[$key] = $this->db->$callback($this->data[$dbkey]);
        }

        return $this->objects[$key];
    }
    
    public function __tostring()
    {
        return get_class($this) + ": " + $this->name;
    }
}

