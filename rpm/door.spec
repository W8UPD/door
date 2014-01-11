%define gitdate   20131111
Name:           door
Version:        1.0.0
Release:        0.2.%{gitdate}git%{?dist}
Summary:        RFID Reader Code

Group:          Applications/System
License:        GPLv2+
URL:            https://github.com/W8UPD/door/
Source0:        %{name}-master.tar.gz
#Source1:        %{name}.service
#Source2:        50-%{name}.conf
BuildArch:      noarch
Requires:       python
Requires:       python-requests
#Requires:       python-RPi-GPIO >= 0.5.2

%description
RFID GPIO Code.

%prep
%setup -q -n door-master

%build
%{__python} setup.py build

%install
mkdir -p %{buildroot}%{_sysconfdir}/%{name}
echo "# Your configuration goes here." > %{buildroot}%{_sysconfdir}/%{name}/config.py
%{__python} setup.py install --root %{buildroot}

install -p -D -m 644 rpm/%{name}.service %{buildroot}/lib/systemd/system/%{name}.service
install -p -D -m 644 rpm/50-%{name}.conf %{buildroot}/etc/rsyslog.d/50-%{name}.conf

mkdir %{buildroot}/%{_bindir}
ln -s %{python_sitelib}/%{name}/rfid.py %{buildroot}/%{_bindir}/rfid.py
chmod +x %{buildroot}%{python_sitelib}/%{name}/rfid.py

%post
/bin/systemctl daemon-reload

%files
%{python_sitelib}/%{name}*
%config(noreplace) %{_sysconfdir}/%{name}/config.py
%{_sysconfdir}/%{name}/config.pyc
%{_sysconfdir}/%{name}/config.pyo
%{_sysconfdir}/rsyslog.d/50-%{name}.conf
/lib/systemd/system/*.service
%{_bindir}/rfid.py

%changelog
* Mon Nov 11 2013 Ricky Elrod <codeblock@fedoraproject.org> - 1.0.0-0.2.20131111git
- Latest upstream master.

* Sat Oct 12 2013 Ricky Elrod <codeblock@fedoraproject.org> - 1.0.0-0.2.20131012git
- Latest upstream master.

* Sat Oct 12 2013 Ricky Elrod <codeblock@fedoraproject.org> - 1.0.0-0.1.20131012git
- Latest upstream master.

* Wed Aug 28 2013 Ricky Elrod <codeblock@fedoraproject.org> - 1.0.0-0.1.20130828git
- Latest upstream master.

* Tue Jun 4 2013 Ricky Elrod <codeblock@fedoraproject.org> - 1.0.0-0.1.20130604git
- Latest upstream master.
- Add syslog file.

* Mon Apr 1 2013 Ricky Elrod <codeblock@fedoraproject.org> - 1.0.0-0.1.20130401gitcdab0de
- Add configuration path.
- Latest upstream master.

* Mon Apr 1 2013 Ricky Elrod <codeblock@fedoraproject.org> - 1.0.0-0.1.20130401gitcdab0de
- Initial build.
