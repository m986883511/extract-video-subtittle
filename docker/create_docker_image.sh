docker stop subtittle
docker rm subtittle
docker build -t m986883511/extract_subtitles .
if [ $? -eq 0 ];then
  echo 'docker build success'
else
  echo 'docker build failed'
  exit 1
fi

docker run -d --name subtittle -p 6666:6666 m986883511/extract_subtitles
if [ $?=0 ];then
  echo 'docker run success'
  echo 'enter container: winpty docker exec -it subtittle sh'
else
  echo 'docker run failed'
  exit 1
fi
