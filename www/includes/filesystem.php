<?php defined('ROOT') ? : die('Access denied');

if ( ! function_exists('glob_recursive'))
{
    // Does not support flag GLOB_BRACE
    
    function glob_recursive($pattern, $flags = 0)
    {
        $files = glob($pattern, $flags);
        
        foreach (glob(dirname($pattern).'/*', GLOB_ONLYDIR|GLOB_NOSORT) as $dir)
        {
            $files = array_merge($files, glob_recursive($dir.'/'.basename($pattern), $flags));
        }
        
        return $files;
    }
}

function get_icon($file_name)
{
    $ext = strtolower(array_pop(explode('.', $file_name)));
    if (file_exists(sprintf(ICON_PATH, $ext)))
    {
       return sprintf(ICON_PATH, $ext);
    }
    elseif (file_exists(sprintf(ICON_PATH, 'file')))
    {
       return sprintf(ICON_PATH, 'file');
    }
    else
    {
        return null;
    }
}
