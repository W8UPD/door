#!/usr/bin/env bash

cwd="$( cd "${BASH_SOURCE[0]%/*}" && pwd )"

if [ "$1" == "clean" ]; then
  rmcommand="rm -rfv $cwd/door-master* $cwd/noarch $cwd/*.src.rpm"
  echo "About to run: $rmcommand"
  echo "Press control-c to abort, or enter to continue."
  read
  $rmcommand
  exit
fi

if [ "$1" == "fetch" ]; then
  wget -O "$cwd"/door-master.tar.gz https://github.com/W8UPD/door/archive/master.tar.gz
  if [ $? == 0 ]; then
    echo "You should now be able to just run ./makerpm.sh to build the RPM"
    exit 0
  else
    echo "Unable to fetch sources. Try again later?"
    exit 1
  fi
fi

rpmbuild --define "_sourcedir $cwd" --define "_rpmdir $cwd" --define "_builddir $cwd" --define "_srcrpmdir $cwd" --define "_speccdir $cwd" -ba "$cwd"/door.spec
rpmbuild --define "_sourcedir $cwd" --define "_rpmdir $cwd" --define "_builddir $cwd" --define "_srcrpmdir $cwd" --define "_speccdir $cwd" -bs "$cwd"/doorcgi.spec

if [ $? == 0 ]; then
  echo "***"
  echo "Done. The output should be somewhere in $cwd"
  echo
  echo "NOTE: doorcgi only produces a .src.rpm. You should use mock or copr"
  echo "      for RHEL6 for building a binary of it that works in production."
  echo
  echo "A copr command might look like this (you must upload the SRPM from"
  echo "above somewhere):"
  echo "   copr-cli build --nowait -r epel-6-x86_64 w8upd-doorcgi <URL OF UPLOADED SRPM>"
  echo "***"
else
  echo "***"
  echo "Something went wrong. Look for errors above and try again."
  echo "***"
fi
