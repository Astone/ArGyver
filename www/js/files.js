function calculate_size(name)
{
    answer = confirm('Are you sure you want to calculate the size of "' + name + '"?\n\nThis might take a long time for with many subfolders or files.');
    return answer;
}

function redirect(url)
{
    document.location = url;
}

function countdown(s)
{
    document.getElementById('timer').innerHTML = s;
    if (s > 1) setTimeout(function(){countdown(s-1)}, 1000);
}

