#!/bin/bash

echo "Making package for $1"

PACKAGE="$1"
PACKAGE_ZIP="$PACKAGE.zip"
PACKAGE_LIB="package-lib-$PACKAGE"
PACKAGE_FOLDER="publish-$PACKAGE"

mkdir -p "$PACKAGE_FOLDER" && \
cp -r lib/* "$PACKAGE_FOLDER" && \
cp -r package/* "$PACKAGE_FOLDER" && \
cd $PACKAGE_LIB && tar -xvf stack.tgz && \
cd ../ && mv $PACKAGE_LIB/stack.tgz ./ && \
cp -r $PACKAGE_LIB/* "$PACKAGE_FOLDER" && \
cd "$PACKAGE_FOLDER" && zip -r "../$PACKAGE_ZIP" .

# # Test compressed size
# maximumsize=52428800
# actualsize=$(wc -c <"$PWD/$PACKAGE_ZIP")
# echo Package size (compressed) is $actualsize bytes
# if [ $actualsize -gt $maximumsize ]; then
#     exit 1
# fi
#
# # Test uncompressed size
# maximumsize=262144000
# actualsize=$(du -hs "$PWD/$PACKAGE_FOLDER" | cut -f 1 -d "   ")
# echo Package size (uncompressed) is $actualsize bytes
# if [ $actualsize -le $maximumsize ]; then
#     exit 2
# fi
