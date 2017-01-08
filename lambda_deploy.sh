#!/bin/bash

[ $# -eq 0 ] && exit 10

FUNCTION="$1"
S3_BUCKET="cowhub-lambda-functions"
S3_KEY_REGISTER="cowhub-image-register/$RANDOM-$RANDOM-$RANDOM"

echo "Deploying $FUNCTION"

echo "BUILDING DOCKER IMAGE"

./build_docker.sh || exit 1

echo "REMOVING PREVIOUS RESULTS"

make clean || exit 5

echo "RUNNING DOCKER IMAGE"

docker run -itd -v "$PWD/package-lib-$FUNCTION":/package-lib \
           cowhub/cowhub-core \
           /bin/bash -c 'cp /stack.tgz /package-lib/' || exit 2

echo "MAKING AND VERIFYING PACKAGE"

./make_and_verify_package.sh $FUNCTION || exit 3

echo "COPYING TO AWS"

aws s3 cp "$FUNCTION.zip" "s3://$S3_BUCKET/$S3_KEY_REGISTER" || exit 4
aws lambda update-function-code \
    --region eu-west-1 \
    --function-name "$FUNCTION" \
    --s3-bucket "$S3_BUCKET" \
    --s3-key "$S3_KEY_REGISTER"

# For verification
mkdir -p verify_package
cd verify_package && unzip "../$FUNCTION.zip"

docker push cowhub/cowhub-core
