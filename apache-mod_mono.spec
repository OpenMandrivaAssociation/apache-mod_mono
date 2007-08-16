%define mod_version 1.2.4

%define xsp_mod_version %mod_version
%define module_path %{_libdir}/apache-extramodules
%define module_name mod_mono

Summary:	Mono module for Apache 2
Name:		apache-mod_mono
Version:	%{mod_version}
Release:	%mkrel 2
License:	Apache License
Group:		System/Servers
URL:		http://www.mono-project.com/downloads/
Source0:	http://www.go-mono.com/sources/mod_mono/%{module_name}-%{mod_version}.tar.bz2
Source1:	http://www.go-mono.com/sources/xsp/xsp-%{xsp_mod_version}.tar.bz2
Patch0:		mod_mono-1.0.4-avoid-version.diff
Patch1:		mod_mono-1.1.17-apache223.patch
Patch2:		mod_mono-1.2.1-mdv.patch
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):	apache-conf >= 2.2.0
Requires(pre):	apache >= 2.2.0
Requires:	apache-conf >= 2.2.0
Requires:	apache >= 2.2.0
BuildRequires:	apache-devel >= 2.2.0
BuildRequires:	mono-devel
BuildRequires:	automake1.7
BuildRequires:	autoconf2.5
BuildRequires:  file
Requires:	mono
BuildRequires:	file
Provides:	apache2-mod_mono
Obsoletes:	apache2-mod_mono
Epoch:		1
BuildRoot:	%{_tmppath}/%{name}-%{version}-root

%description
This is an experimental module that allows you to run ASP.NET
pages on Unix with Apache and Mono.
It includes some aspx C# scripts for testing.
Please read the included INSTALL file for how to get the mod-mono
server running.

%prep

%setup -q -n %{module_name}-%{mod_version} -a 1
%patch0 -p0
%patch1 -p1 -b .apache223
%patch2 -p1 -b .mdv

%build
export WANT_AUTOCONF_2_5=1
rm -f configure
libtoolize --copy --force; aclocal-1.7; automake-1.7 --add-missing --copy; autoconf --force

# Build sample ASP.NET pages from xsp distribution
pushd xsp-%{xsp_mod_version}
%configure2_5x
make
popd

# Build Apache Module
export CPPFLAGS="`apr-1-config --cppflags`"
%configure2_5x \
    --with-apxs=%{_sbindir}/apxs \
    --with-apr-config=%{_bindir}/apr-1-config
make

%install
rm -fr %{buildroot}

pushd xsp-%{xsp_mod_version}
%makeinstall_std
%if %_lib != lib
mv %buildroot%_libdir/xsp/* %buildroot%_prefix/lib/xsp
%endif
popd

install -d 755 %{buildroot}%{_sysconfdir}/httpd/modules.d
install -d 755 %{buildroot}%{module_path}
install -d 755 %{buildroot}%{_var}/www/mono
install -d 755 %{buildroot}%{_var}/www/.wapi
install -d 755 %{buildroot}%{_localstatedir}/%{name}

# Mono Configuration for Apache
install -m 644 mod_mono.conf %{buildroot}%{_sysconfdir}/httpd/modules.d/91_mod_mono.conf
# add examples
echo "    Alias /mono \"%{_defaultdocdir}/%{name}-%{mod_version}/test\"" >> %{buildroot}%{_sysconfdir}/httpd/modules.d/91_mod_mono.conf


install src/.libs/mod_mono.so %{buildroot}%{module_path}/mod_mono.so
install -D man/mod_mono.8 %{buildroot}%{_mandir}/man8/mod_mono.8

# strip away annoying ^M
find %{buildroot} -type f|xargs file|grep 'CRLF'|cut -d: -f1|xargs perl -p -i -e 's/\r//'
find %{buildroot} -type f|xargs file|grep 'text'|cut -d: -f1|xargs perl -p -i -e 's/\r//'

%post
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi
    
%postun
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
	%{_initrddir}/httpd restart 1>&2
    fi
fi
		    
%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}
		    
%files
%defattr(-,root,root)
%doc ChangeLog COPYING INSTALL NEWS README xsp-%{xsp_mod_version}/test
%attr(0755,root,root) %{_bindir}/*
%attr(0644,root,root) %config(noreplace)  %{_sysconfdir}/httpd/modules.d/91_mod_mono.conf
%attr(0755,root,root) %{module_path}/mod_mono.so
%attr(0644,root,root) %{_mandir}/man1/*
%attr(0644,root,root) %{_mandir}/man8/mod_mono.8*
%_libdir/pkgconfig/*
%_prefix/lib/xsp
%_prefix/lib/mono/?.0/*
%_prefix/lib/mono/gac/*
%defattr(-,apache,apache)
%dir %{_var}/www/mono
%dir %{_var}/www/.wapi
%dir %attr(0755,apache,apache) %{_localstatedir}/%{name}



