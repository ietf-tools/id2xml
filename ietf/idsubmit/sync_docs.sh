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
                        --ssh_key_path=*)
                                ssh_key_path=`echo "$arg" | sed -e 's/^[^=]*=//'`
                        ;;
                        --remote_web1=*)
                                remote_web1=`echo "$arg" | sed -e 's/^[^=]*=//'`
                        ;;
                        --remote_ftp1=*)
                                remote_ftp1=`echo "$arg" | sed -e 's/^[^=]*=//'`
                        ;;
                        --remote_web2=*)
                                remote_web2=`echo "$arg" | sed -e 's/^[^=]*=//'`
                        ;;
                        --remote_ftp2=*)
                                remote_ftp2=`echo "$arg" | sed -e 's/^[^=]*=//'`
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
# End Edit Section

staging_path=""
local_path=""
revision=""
filename=""
ssh_key_path=""

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
if [ -z $ssh_key_path ];then
        usage "ssh_key_path"; exit;
fi
if [ $local_path ];then
	$EXEC_CP $staging_path/$filename-$revision.*  $local_path/
fi
if [ $remote_web1 ];then
	$EXEC_SCP -p -i $ssh_key_path $staging_path/$filename-$revision.* \
		$remote_web1
fi
if [ $remote_web2 ];then
$EXEC_SCP -p -i $ssh_key_path $staging_path/$filename-$revision.* \
	$remote_web2
fi
if [ $remote_ftp1 ];then
$EXEC_SCP -p -i $ssh_key_path $staging_path/$filename-$revision.* \
	$remote_ftp1
fi
if [ $remote_ftp2 ];then
$EXEC_SCP -p -i $ssh_key_path $staging_path/$filename-$revision.* \
	$remote_ftp2
fi
# END
