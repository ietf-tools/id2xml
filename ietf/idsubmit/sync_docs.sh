#!/bin/sh

usage ()
{
	if [ ! -z "$@" ];then
		echo "[Error] '--"$@"' is missing"
		echo ""
	fi

	echo "Usage:" $0 "
	--staging_path=<staging_path>
	--target_path_web=<target_path_web>
	--target_path_ftp=<target_path_ftp>
	--revision=<revision>
	--filename=<filename>
	[--is_development=<is_development>]
	"

}

parse_options ()
{
	for arg do
		case $arg in
			--staging_path=*)
				staging_path=`echo "$arg" | sed -e 's/^[^=]*=//'`
			;;
			--target_path_web=*)
				target_path_web=`echo "$arg" | sed -e 's/^[^=]*=//'`
			;;
			--target_path_ftp=*)
				target_path_ftp=`echo "$arg" | sed -e 's/^[^=]*=//'`
			;;
			--revision=*)
				revision=`echo "$arg" | sed -e 's/^[^=]*=//'`
			;;
			--filename=*)
				filename=`echo "$arg" | sed -e 's/^[^=]*=//'`
			;;
			--is_development=*)
				is_development=`echo "$arg" | sed -e 's/^[^=]*=//'`
				if [ "$is_development" = "1" ];then
					is_development=1
				fi
			;;

		esac
	done
}

EXEC_SCP=/usr/bin/scp
EXEC_CP=cp

staging_path=""
target_path_web=""
target_path_ftp=""
revision=""
filename=""
is_development=0

# BEGIN
parse_options $*

if [ -z $staging_path ];then
	usage "staging_path"; exit;
fi

if [ -z $target_path_web ];then
	usage "target_path_web"; exit;
fi

if [ -z $target_path_ftp ];then
	usage "target_path_ftp"; exit;
fi

if [ -z $revision ];then
	usage "revision"; exit;
fi

if [ -z $filename ];then
	usage "filename"; exit;
fi

# set options whether is production or not
if [ "$is_development" = 1 ];then
	identity="/home/mirror/.ssh/id_dsa"
	target_server_web="mirror@chiedprweb1.nc.neustar.com ietf@stiedprstage1.va.neustar.com"
	target_server_ftp="mirror@chiedprftp1.nc.neustar.com mirror@stiedprftp1.va.neustar.com"
else
	identity="/home/ietf/.ssh/identity-new"
	target_server_web="mirror@chiedprweb1 ietf@stiedprstage1"
	target_server_ftp="mirror@chiedprftp1 mirror@stiedprftp1"
fi

if [ "$is_development" = "1" ];then
	$EXEC_SCP -p -i /home/mirror/.ssh/id_dsa $staging_path/$filename-$revision.* \	
		ietf@stiedprstage1.va.neustar.com:$target_path_web/
	$EXEC_SCP -p -i /home/mirror/.ssh/identity-new $staging_path/$filename-$revision.* \
		mirror@chiedprweb1.nc.neustar.com:$target_path_web/
	$EXEC_SCP -p -i /home/mirror/.ssh/identity-new $staging_path/$filename-$revision.* \
		mirror@stiedprftp1.va.neustar.com:$target_path_ftp/
	$EXEC_SCP -p -i /home/mirror/.ssh/identity-new $staging_path/$filename-$revision.* \
		mirror@chiedprftp1.nc.neustar.com:$target_path_ftp/

else
	$EXEC_CP $staging_path/$filename-$revision.*  $target_path_web/
	$EXEC_SCP -p -i /home/ietf/.ssh/identity-new $staging_path/$filename-$revision.* \
		mirror@stiedprweb1:$target_path_web/
	$EXEC_SCP -p -i /home/ietf/.ssh/identity-new $staging_path/$filename-$revision.* \
		mirror@chiedprweb1:$target_path_web/
	$EXEC_SCP -p -i /home/ietf/.ssh/identity-new $staging_path/$filename-$revision.* \
		mirror@stiedprftp1:$target_path_ftp/
	$EXEC_SCP -p -i /home/ietf/.ssh/identity-new $staging_path/$filename-$revision.* \
		mirror@chiedprftp1:$target_path_ftp/
fi

# END
