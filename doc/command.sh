echo '  1: sphinx-quickstart'
echo '  2: make html'
echo '  3: make epub'
echo '  4: make latexpdf'
read -n 1 -p "enter a digit to switch command > " number
printf "\n"

cd $(dirname $0)
echo your system: `uname -s`
uname -s | grep NT
if [ $? -eq 0 ];then
  current_dir=`cygpath -w $(pwd)`
  winpty='winpty'
else
  current_dir=`cygpath -u $(pwd)`
  winpty=''
fi
echo current path: $current_dir


if [ "$number" = 1 ];then
  $winpty docker run -it --rm -v $current_dir:/docs sphinxdoc/sphinx sphinx-quickstart
elif [ "$number" = 2 ];then
  $winpty docker run -it --rm -v $current_dir:/docs sphinxdoc/sphinx make html
elif [ "$number" = 3 ];then
  $winpty docker run -it --rm -v $current_dir:/docs sphinxdoc/sphinx make epub
elif [ "$number" = 4 ];then
  $winpty docker run -it --rm -v $current_dir:/docs sphinxdoc/sphinx-latexpdf make latexpdf
else
  echo 'Error Input! Failed!'
  echo 'Error Input! Failed!'
  echo 'Error Input! Failed!'
  exit 1
fi

if [ $? -ne 0 ];then
  echo 'Exceute docker command failed.'
  exit 1
fi
