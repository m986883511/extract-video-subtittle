port=9001

echo '  1: sphinx-quickstart'
echo '  2: make html'
echo '  3: make epub'
echo '  4: make latexpdf'
echo "  5: sphinx-autobuild at $port"

if [ ! -n "$1" ];then
  read -n 1 -p "enter a digit to switch command > " number
  printf "\n"
else
  number="$1"
fi


cd $(dirname $0)
echo your system: `uname -s`
cd ..
uname -s | grep NT
if [ $? -eq 0 ];then
  project_dir=`cygpath -w $(pwd)`
  winpty='winpty'
else
  project_dir=`pwd`
  winpty=''
fi
echo project_dir path: $project_dir


if [ "$number" = 1 ];then
  $winpty docker run -it --rm -v $project_dir:/docs --name sphinx m986883511/sphinx:all sphinx-quickstart
elif [ "$number" = 2 ];then
  $winpty docker run -it --rm -v $project_dir:/docs --name sphinx m986883511/sphinx:all make -C docs html
elif [ "$number" = 3 ];then
  $winpty docker run -it --rm -v $project_dir:/docs --name sphinx m986883511/sphinx:all make -C docs epub
elif [ "$number" = 4 ];then
  $winpty docker run -it --rm -v $project_dir:/docs --name sphinx m986883511/sphinx:all make -C docs latexpdf
elif [ "$number" = 5 ];then
  echo ">>> $winpty docker run -it --rm -v $project_dir:/docs -p $port:$port --name sphinx m986883511/sphinx:all sphinx-autobuild docs/source docs/build/html --port $port"
  $winpty docker run -it --rm -v $project_dir:/docs -p $port:$port --name sphinx m986883511/sphinx:all sphinx-autobuild docs/source docs/build/html --port $port --host 0.0.0.0
else
  echo 'Error Input! Failed!'
  exit 1
fi

if [ $? -ne 0 ];then
  echo 'Execute docker command failed.'
  exit 1
fi
