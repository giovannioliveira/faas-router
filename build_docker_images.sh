docker build ./functions/f -t giovanniapsoliveira/faas-router-f
docker build ./functions/g -t giovanniapsoliveira/faas-router-g
docker build ./functions/h -t giovanniapsoliveira/faas-router-h
docker build ./functions/hb -t giovanniapsoliveira/faas-router-hb

docker push giovanniapsoliveira/faas-router-f:latest
docker push giovanniapsoliveira/faas-router-g:latest
docker push giovanniapsoliveira/faas-router-h:latest
docker push giovanniapsoliveira/faas-router-hb:latest
