Summary:	Serial console server daemon/client
Name:		conserver
Version:	8.1.18
Release:	5
License:	BSD-like
Group:		System/Servers
URL:		http://www.conserver.com/
Source0:	http://www.conserver.com/%{name}-%{version}.tar.gz
Source1:	%{name}.service
Source2:	%{name}.sysconfig
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires:	tcp_wrappers
BuildRequires:	openssl-devel
BuildRequires:	pam-devel
BuildRequires:	tcp_wrappers-devel
BuildRequires:	gssglue-devel

Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units

%description
Conserver is an application that allows multiple users to watch a serial
console at the same time. It can log the data, allows users to take
write-access of a console (one at a time), and has a variety of bells and
whistles to accentuate that basic functionality.

%package daemon
Summary:	Serial console server daemon
Group:		System/Servers
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires:	tcp_wrappers

Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units

%description daemon
Conserver is an application that allows multiple users to watch a serial
console at the same time. It can log the data, allows users to take
write-access of a console (one at a time), and has a variety of bells and
whistles to accentuate that basic functionality.

This package contains the server daemon part.

%package client
Summary:	Serial console server client
Group:		System/Servers
Requires:	tcp_wrappers

%description client
Conserver is an application that allows multiple users to watch a serial
console at the same time. It can log the data, allows users to take
write-access of a console (one at a time), and has a variety of bells and
whistles to accentuate that basic functionality.

This package contains the client part.


%prep

%setup -q

# lib64 fixes
perl -pi -e "s|/lib\b|/%{_lib}|g" configure*


%build

%configure2_5x \
    --with-port=782 \
    --with-base=0 \
    --with-master=console \
    --with-cffile=%{_sysconfdir}/%{name}.cf \
    --with-pwdfile=%{_sysconfdir}/%{name}.passwd \
    --with-logfile=/var/log/%{name}/%{name}.log \
    --with-pidfile=/var/run/%{name}/%{name}.pid \
    --with-libwrap=%{_prefix} \
    --with-openssl=%{_prefix} \
    --with-uds=%{_localstatedir}/lib/%{name} \
    --with-maxmemb=16 \
    --with-timeout=10 \
    --with-pam \
    --with-gssapi

%make

# make test must be run by root?

%install

%makeinstall

install -d %{buildroot}%{_sysconfdir}/sysconfig
install -d %{buildroot}/var/log/%{name}
install -d %{buildroot}/var/run/%{name}
install -d %{buildroot}/var/consoles
install -d %{buildroot}%{_localstatedir}/lib/%{name}

%{__sed} -e 's/^/#/' \
  < %{name}.cf/%{name}.cf \
  > %{buildroot}%{_sysconfdir}/%{name}.cf
%{__sed} -e 's/^/#/' \
  < %{name}.cf/%{name}.passwd \
  > %{buildroot}%{_sysconfdir}/%{name}.passwd

install -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service
install -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/%{name}

# fix ghostfiles
touch %{buildroot}/var/log/%{name}/%{name}.log

# remove crap
rm -f %{buildroot}%{_sysconfdir}/%{name}.rc
rm -rf %{buildroot}%{_datadir}/examples

# install missing stuff
install -m 755 conserver/convert %{buildroot}%{_sbindir}/convert-conserver.cf

# nuke dupe
rm -f %{buildroot}%{_libdir}/conserver/convert

%post -n %{name}-daemon
%systemd_post conserver.service
%create_ghostfile /var/log/%{name}/%{name}.log root root 0644

#make sure /etc/services has a conserver entry
if ! grep -E '\<conserver\>' /etc/services > /dev/null 2>&1 ; then
  echo "console		782/tcp		conserver" >> /etc/services
fi

%preun -n %{name}-daemon
%systemd_preun conserver.service

%postun
%systemd_postun_with_restart conserver.service

%clean

%files daemon
%doc CHANGES FAQ LICENSE README TODO %{name}.html
%doc %{name}.cf/%{name}.cf
%doc %{name}.cf/%{name}.passwd
%doc %{name}.cf/label.ps
%doc %{name}.cf/test.cf
%doc %{name}/Sun-serial
%config(noreplace) %{_sysconfdir}/%{name}.cf
%config(noreplace) %{_sysconfdir}/%{name}.passwd
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%{_unitdir}/%{name}.service
%{_mandir}/man8/%{name}.8*
%{_mandir}/man5/%{name}.cf.5*
%{_mandir}/man5/%{name}.passwd.5*
%{_sbindir}/%{name}
%{_sbindir}/convert-conserver.cf
%dir /var/log/%{name}
%dir /var/run/%{name}
%dir /var/consoles
%dir %{_localstatedir}/lib/%{name}
%attr(0644,root,root) %ghost /var/log/%{name}/%{name}.log

%files client
%{_bindir}/console
%{_mandir}/man1/console.1*
