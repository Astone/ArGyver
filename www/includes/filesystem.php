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

function pretty_file_size($size)
{
    if ($size === null) return '?';
    if ($size > 1000 * pow(2, 40)) return sprintf("%.2f PB", $size / pow(2, 50));
    if ($size > 1000 * pow(2, 30)) return sprintf("%.2f TB", $size / pow(2, 40));
    if ($size > 1000 * pow(2, 20)) return sprintf("%.2f GB", $size / pow(2, 30));
    if ($size > 1000 * pow(2, 10)) return sprintf("%.2f MB", $size / pow(2, 20));
    if ($size > 1000 * pow(2,  0)) return sprintf("%.2f KB", $size / pow(2, 10));
    return sprintf("%d B&nbsp;&nbsp;", $size);
}

