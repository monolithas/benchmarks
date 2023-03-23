#!/bin/bash

LANGUAGES=('gpp','gcc','gnat','rust');

ZIPNAME=benchmarksgame-sourcecode.zip;
SOURCECODE=https://salsa.debian.org/benchmarksgame-team/benchmarksgame/-/raw/master/public/download/${ZIPNAME};

# TEST TEST
rm -rf tmp/*

# download the above file and pass the path as the only argument 
# to this script. This script will:
#   1. Unzip the file to a tmp directory
#   2. Find all code files in the above file
#   3. Generate `fetch` commands for a download script

# install the unzip tool
sudo apt install -y unzip;

# create and move to working directory
pushd . && mkdir -p tmp && cd tmp;

# download the source code package
wget ${SOURCECODE};

# extract the source code
unzip ${ZIPNAME} > /dev/null;

# find all files with extensions in LANGUAGES list
FILES=( $( find ./ -type f \( -iname \*.gpp -o -iname \*.gcc -o -iname \*.gnat -o -iname \*.rust \) ) );

for file in "${FILES[@]}"; do
    name=${file##*/};
    bench=${name%%\.*};
    lang=${name##*.};

    tmp=${name/${bench}/};
    tmp=${tmp/${lang}/};
    tmp=${tmp#*\.};
    tmp=${tmp#*\-};
    tmp=${tmp%%\.*};

    if [[ -z "${tmp// }" ]]; then
        tmp=1;
    fi

    count=$tmp;
    echo "poetry run fetch -- -r=3 -n=\"${bench}-${lang}-${count}\"";
done

# return to root directory
popd;

# clean up
rm -rf tmp/*