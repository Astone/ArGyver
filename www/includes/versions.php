<?php defined('ROOT') ? : die('Access denied');

if ($vid = get('vid'))
{
    define('MIN_V', $vid);
    define('MAX_V', $vid);
}
else
{
    if ( ! isset($_SESSION['MAX_V']) || ! isset($_SESSION['MIN_V']))
    {

        $aid = get('aid', 1);
        $archive = get_archive($aid);
        if ($archive && $archive->exists() && $iterations = $archive->get_iterations())
	{
            $last = array_pop($iterations);
            $_SESSION['MAX_V'] = $last['id'];

            $v = $last;
            while ( ! empty($iterations) && $last['start'] - $v['start'] < TIME_WINDOW *86400)
            {
                $v = array_pop($iterations);
            }
            $_SESSION['MIN_V'] = $v['id'];
        }
        else
        {
            $_SESSION['MAX_V'] = null;
            $_SESSION['MIN_V'] = null;
        }
    }

    if ($min_v = get('min_vid')) $_SESSION['MIN_V'] = $min_v;
    if ($max_v = get('max_vid')) $_SESSION['MAX_V'] = max($min_v, $max_v);

    define('MIN_V', $_SESSION['MIN_V']);
    define('MAX_V', $_SESSION['MAX_V']);
}
