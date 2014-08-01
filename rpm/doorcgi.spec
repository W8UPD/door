%define gitdate    20140801
Name:           doorcgi
Version:        1.0.0
Release:        1.%{gitdate}git%{?dist}
Summary:        The server side of the W8UPD RFID log system

Group:          Applications/Internet
License:        GPLv2+
URL:            https://github.com/w8upd/door/
# Source0 retrieved by pulling a Github tarball.
# See: https://github.com/w8upd/door/downloads
Source0:        master.tar.gz
BuildRequires:  ghc-cabal-install
BuildRequires:  mysql-devel

%description
This is the web UI for handling logging from the RFID reader Python code.

%prep
%setup -q -n door-master

%build
cd doorcgi
cabal sandbox init
cabal build
cabal install

%check

%install
mkdir -p %{buildroot}/%{_bindir}
cd doorcgi
cp .cabal-sandbox/bin/%{name} %{buildroot}/%{_bindir}/%{name}
install -D -m 0644 %{name}.conf.example %{buildroot}/%{_sysconfdir}/%{name}.conf

%files
%config(noreplace) %{_sysconfdir}/doorcgi.conf
%{_bindir}/%{name}

%changelog
* Fri Aug 1 2014 Ricky Elrod <codeblock@fedoraproject.org> - 1.0.0-1.20140801git
- Rewrite in Scotty.

* Wed Nov 13 2013 Ricky Elrod <codeblock@fedoraproject.org> - 0.0.1-1.20131113git
- Log entries via UDP.

* Sat Oct 12 2013 Ricky Elrod <codeblock@fedoraproject.org> - 0.0.1-1.20131012git
- Initial build.
