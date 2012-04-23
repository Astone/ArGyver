<?php defined('ROOT') ? : die('Access denied to '. __FILE__);

class DbObject
{
    public $id = null;
    public $name = null;
    protected $db = null;
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

        $value = $this->data[$dbkey];

        $value = is_string($value) ? utf8_decode($value) : $value;

        if (empty($callback)) return $value;

        $cachekey = $key.'|'.$callback;

        if (array_key_exists($dbkey, $this->data) && ! array_key_exists($cachekey, $this->objects))
        {
            $this->objects[$cachekey] = $this->db->$callback($value);
        }

        return $this->objects[$key.'|'.$callback];
    }

    public function reset()
    {
        unset($this->objects);
        $this->objects = Array();
    }

    public function __tostring()
    {
        return get_class($this) . ": " . $this->name;
    }
}

