Summary:	Serial console server daemon/client
Name:		conserver
Version:	8.1.18
Release:	%mkrel 1
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
BuildRequires:	gssglue-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}

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

cp %{SOURCE1} %{name}.init
cp %{SOURCE2} %{name}.sysconfig

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
rm -rf %{buildroot}

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
rm -rf %{buildroot}

%files daemon
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

%files client
%defattr(-,root,root)
%{_bindir}/console
%{_mandir}/man1/console.1*


%changelog
* Mon Nov 15 2010 Oden Eriksson <oeriksson@mandriva.com> 8.1.18-1mdv2011.0
+ Revision: 597622
- 8.1.18

* Wed Apr 21 2010 Funda Wang <fwang@mandriva.org> 8.1.17-3mdv2010.1
+ Revision: 537383
- rebuild

* Sun Jan 17 2010 Guillaume Rousse <guillomovitch@mandriva.org> 8.1.17-2mdv2010.1
+ Revision: 492663
- spec cleanup

* Wed Sep 30 2009 Oden Eriksson <oeriksson@mandriva.com> 8.1.17-1mdv2010.0
+ Revision: 451322
- 8.1.17

* Wed Sep 02 2009 Thierry Vignaud <tv@mandriva.org> 8.1.16-6mdv2010.0
+ Revision: 424944
- rebuild

* Wed Jul 23 2008 Thierry Vignaud <tv@mandriva.org> 8.1.16-5mdv2009.0
+ Revision: 243628
- rebuild

  + Pixel <pixel@mandriva.com>
    - adapt to %%_localstatedir now being /var instead of /var/lib (#22312)

* Tue Feb 19 2008 Oden Eriksson <oeriksson@mandriva.com> 8.1.16-3mdv2008.1
+ Revision: 172963
- more fixes...

* Tue Feb 19 2008 Oden Eriksson <oeriksson@mandriva.com> 8.1.16-2mdv2008.1
+ Revision: 172959
- fix a silly bug (duh!)
- don't start it per default

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Wed Apr 18 2007 Oden Eriksson <oeriksson@mandriva.com> 8.1.16-1mdv2008.0
+ Revision: 14791
- 8.1.16


* Fri Dec 22 2006 Oden Eriksson <oeriksson@mandriva.com> 8.1.14-1mdv2007.0
+ Revision: 101626
- Import conserver

* Tue Apr 11 2006 Oden Eriksson <oeriksson@mandriva.com> 8.1.14-1mdk
- 8.1.14

* Tue Jan 17 2006 Oden Eriksson <oeriksson@mandriva.com> 8.1.13-1mdk
- 8.1.13

* Wed Nov 30 2005 Oden Eriksson <oeriksson@mandriva.com> 8.1.11-2mdk
- rebuilt against openssl-0.9.8a

* Sat Apr 16 2005 Lenny Cartier <lenny@mandrakesoft.com> 8.1.11-1mdk
- 8.1.11

* Sat Oct 09 2004 Lenny Cartier <lenny@mandrakesoft.com> 8.1.10-1mdk
- 8.1.10
- bzip2 source

* Fri Aug 06 2004 Erwan Velu <erwan@mandrakesoft.com> 8.1.9-1mdk
- 8.1.9

* Sat Jun 12 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 8.1.8-1mdk
- 8.1.8

* Sun May 30 2004 Oden Eriksson <oeriksson@mandrakesoft.com> 8.1.7-1mdk
- 8.1.7

* Fri May 28 2004 Lenny Cartier <lenny@mandrakesoft.com> 8.1.6-1mdk
- 8.1.6

* Thu Apr 15 2004 Michael Scherer <misc@mandrake.org> 8.1.4-1mdk
- New release 8.1.4
- rpmbuildupdate aware

