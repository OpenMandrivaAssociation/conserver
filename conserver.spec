Summary:	Serial console server daemon/client
Name:		conserver
Version:	8.1.16
Release:	%mkrel 6
License:	BSD-like
Group:		System/Servers
URL:		http://www.conserver.com/
Source0:	http://www.conserver.com/%{name}-%{version}.tar.gz
Source1:	%{name}.init
Source2:	%{name}.sysconfig
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires:	tcp_wrappers
BuildRequires:	openssl-devel
BuildRequires:	pam-devel
BuildRequires:	tcp_wrappers-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Conserver is an application that allows multiple users to watch a serial
console at the same time. It can log the data, allows users to take
write-access of a console (one at a time), and has a variety of bells and
whistles to accentuate that basic functionality.

%package -n	conserver-daemon
Summary:	Serial console server daemon
Group:		System/Servers
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires:	tcp_wrappers

%description -n	conserver-daemon
Conserver is an application that allows multiple users to watch a serial
console at the same time. It can log the data, allows users to take
write-access of a console (one at a time), and has a variety of bells and
whistles to accentuate that basic functionality.

This package contains the server daemon part.

%package -n	conserver-client
Summary:	Serial console server client
Group:		System/Servers
Requires:	tcp_wrappers

%description -n	conserver-client
Conserver is an application that allows multiple users to watch a serial
console at the same time. It can log the data, allows users to take
write-access of a console (one at a time), and has a variety of bells and
whistles to accentuate that basic functionality.

This package contains the client part.

%prep

%setup -q

cp %{SOURCE1} %{name}.init
cp %{SOURCE2} %{name}.sysconfig

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
    --with-pam

%make

# make test must be run by root?

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%makeinstall

install -d %{buildroot}%{_initrddir}
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

install -m0755 %{name}.init %{buildroot}%{_initrddir}/%{name}
install -m0644 %{name}.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/%{name}

# fix ghostfiles
touch %{buildroot}/var/log/%{name}/%{name}.log

# remove crap
rm -f %{buildroot}%{_sysconfdir}/%{name}.rc
rm -rf %{buildroot}%{_datadir}/examples

# install missing stuff
install -m0755 conserver/convert %{buildroot}%{_sbindir}/convert-conserver.cf

# nuke dupe
rm -f %{buildroot}%{_libdir}/conserver/convert

%post -n %{name}-daemon
%_post_service %{name}
%create_ghostfile /var/log/%{name}/%{name}.log root root 0644

# make sure /etc/services has a conserver entry
if ! egrep '\<conserver\>' /etc/services > /dev/null 2>&1 ; then
  echo "console		782/tcp		conserver" >> /etc/services
fi

%preun -n %{name}-daemon
%_preun_service %{name}

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files -n %{name}-daemon
%defattr(-,root,root)
%doc CHANGES FAQ LICENSE README TODO %{name}.html
%doc %{name}.cf/%{name}.cf
%doc %{name}.cf/%{name}.passwd
%doc %{name}.cf/label.ps
%doc %{name}.cf/test.cf
%doc %{name}/Sun-serial
%config(noreplace) %{_sysconfdir}/%{name}.cf
%config(noreplace) %{_sysconfdir}/%{name}.passwd
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%attr(0755,root,root) %{_initrddir}/%{name}
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

%files -n %{name}-client
%defattr(-,root,root)
%{_bindir}/console
%{_mandir}/man1/console.1*
