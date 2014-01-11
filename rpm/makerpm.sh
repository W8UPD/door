#!/usr/bin/env bash

cwd="$( cd "${BASH_SOURCE[0]%/*}" && pwd )"

rpmbuild --define "_sourcedir ." --define "_rpmdir ." --define "_builddir `pwd`" --define "_srcrpmdir ." --define "_speccdir ." -ba "$cwd"/door.spec

if [ $? == 0 ]; then
  echo "***"
  echo "Done. The output should be somewhere in $cwd/noarch"
  echo "***"
else
  echo "***"
  echo "Something went wrong. Look for errors above and try again."
  echo "***"
fi
