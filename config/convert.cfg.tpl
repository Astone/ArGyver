[options]
rsync_options: -rlpEtgoHDhuyv --delete-excluded --exclude=.git --exclude=Thumbs.db --exclude=desktop.ini --exclude=AlbumArt_*.* --exclude=\~\$* --exclude=archive --exclude=\~*.tmp

[server]
root        : /home/amethist/backup_new/
snapshot    : snapshot/
archive     : archive/
repository  : .data/
database    : .data.sqlite
tmp         : .tmp/

[sources]

