#!/bin/sh

usage ()
{
	if [ ! -z "$@" ];then
		echo "[Error] '--"$@"' is missing"
		echo ""
	fi

	echo "Usage:" $0 "
	--staging_path=<staging_path>
	--revision=<revision>
	--filename=<filename>
	[--local_path=<local_path>]
	"

}

parse_options ()
{
	for arg do
		case $arg in
			--staging_path=*)
				staging_path=`echo "$arg" | sed -e 's/^[^=]*=//'`
			;;
			--revision=*)
				revision=`echo "$arg" | sed -e 's/^[^=]*=//'`
			;;
			--filename=*)
				filename=`echo "$arg" | sed -e 's/^[^=]*=//'`
			;;
			--local_path=*)
				local_path=`echo "$arg" | sed -e 's/^[^=]*=//'`
			;;

		esac
	done
}
# Edit followings for each local environment
EXEC_SCP="/usr/bin/scp -P 65321"
#EXEC_SCP=/usr/bin/scp # When a special port is not needed
EXEC_CP=cp
SSH_KEY_PATH="/home/mlee/.ssh/id_dsa"
REMOTE_WEB1_PATH="leemich@usa.ultrawhb.com:web-path"
#REMOTE_WEB2_PATH="leemich@usa.ultrawhb.com:web-path"
REMOTE_FTP1_PATH="leemich@usa.ultrawhb.com:ftp-path"
#REMOTE_FTP2_PATH="leemich@usa.ultrawhb.com:ftp-path"
# End Edit Section

staging_path=""
local_path=""
revision=""
filename=""

# BEGIN
parse_options $*

if [ -z $staging_path ];then
	usage "staging_path"; exit;
fi

if [ -z $revision ];then
	usage "revision"; exit;
fi

if [ -z $filename ];then
	usage "filename"; exit;
fi

if [ $local_path ];then
	$EXEC_CP $staging_path/$filename-$revision.*  $local_path/
fi
if [ $REMOTE_WEB1_PATH ];then
	$EXEC_SCP -p -i $SSH_KEY_PATH $staging_path/$filename-$revision.* \
		$REMOTE_WEB1_PATH
fi
if [ $REMOTE_WEB2_PATH ];then
$EXEC_SCP -p -i $SSH_KEY_PATH $staging_path/$filename-$revision.* \
	$REMOTE_WEB2_PATH
fi
if [ $REMOTE_FTP1_PATH ];then
$EXEC_SCP -p -i $SSH_KEY_PATH $staging_path/$filename-$revision.* \
	$REMOTE_FTP1_PATH
fi
if [ $REMOTE_FTP2_PATH ];then
$EXEC_SCP -p -i $SSH_KEY_PATH $staging_path/$filename-$revision.* \
	$REMOTE_FTP2_PATH
fi
# END
