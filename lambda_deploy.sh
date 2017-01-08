#!/bin/bash

# FUNCTION="$1"
FUNCTION_REGISTER='cowhub-image-register'
FUNCTION_MATCH='cowhub-image-match'
FUNCTION_COMPARE='cowhub-image-compare'
S3_BUCKET="cowhub-lambda-functions"
S3_KEY="cowhub-image-register/$RANDOM-$RANDOM-$RANDOM"

echo "Deploying $FUNCTION"

echo "BUILDING DOCKER IMAGE"

./build_docker.sh || exit 1

echo "REMOVING PREVIOUS RESULTS"

make clean || exit 5

echo "RUNNING DOCKER IMAGE"

docker run -itd -v "$PWD/package-lib":/package-lib \
           cowhub/cowhub-core \
           /bin/bash -c 'cp /stack.tgz /package-lib/' || exit 2

echo "MAKING AND VERIFYING PACKAGE"

./make_and_verify_package.sh || exit 3

echo "COPYING TO AWS"

aws s3 cp "publish.zip" "s3://$S3_BUCKET/$S3_KEY" || exit 4
aws lambda update-function-code \
    --region eu-west-1 \
    --function-name "$FUNCTION_REGISTER" \
    --s3-bucket "$S3_BUCKET" \
    --s3-key "$S3_KEY"
aws lambda update-function-code \
    --region eu-west-1 \
    --function-name "$FUNCTION_MATCH" \
    --s3-bucket "$S3_BUCKET" \
    --s3-key "$S3_KEY"
aws lambda update-function-code \
    --region eu-west-1 \
    --function-name "$FUNCTION_COMPARE" \
    --s3-bucket "$S3_BUCKET" \
    --s3-key "$S3_KEY"

# For verification
mkdir -p verify_package
cd verify_package && unzip "../publish.zip"

docker push cowhub/cowhub-core
