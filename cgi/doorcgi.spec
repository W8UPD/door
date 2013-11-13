%define gitdate    20131113
Name:           doorcgi
Version:        0.0.1
Release:        1.%{gitdate}git%{?dist}
Summary:        The server side of the W8UPD RFID log system

Group:          Applications/Internet
License:        GPLv2+
URL:            https://github.com/w8upd/door/
# Source0 retrieved by pulling a Github tarball.
# See: https://github.com/w8upd/door/downloads
Source0:        master.tar.gz
BuildRequires:  ghc-cgi-devel
BuildRequires:  ghc-convertible-devel
BuildRequires:  ghc-HDBC-devel
BuildRequires:  ghc-HDBC-mysql-devel
BuildRequires:  ghc-configurator-devel
BuildRequires:  ghc-unix-compat-devel
BuildRequires:  mysql-devel

%description
This is the CGI for handling logging from the RFID reader Python code.

%prep
%setup -q -n door-master

%build
ghc -threaded --make -o logrfid.cgi doorcgi.hs

%check

%install
mkdir -p %{buildroot}/srv/www/door.w8upd.org/
install -D -m 0755 cgi/logrfid.cgi %{buildroot}/srv/www/door.w8upd.org/logrfid.cgi
install -D -m 0644 cgi/doorcgi.conf.example %{buildroot}/%{_sysconfdir}/doorcgi.conf

%files
%config(noreplace) %{_sysconfdir}/doorcgi.conf
/srv/www/door.w8upd.org/logrfid.cgi

%changelog
* Wed Nov 13 2013 Ricky Elrod <codeblock@fedoraproject.org> - 0.0.1-1.20131113git
- Log entries via UDP.

* Sat Oct 12 2013 Ricky Elrod <codeblock@fedoraproject.org> - 0.0.1-1.20131012git
- Initial build.
